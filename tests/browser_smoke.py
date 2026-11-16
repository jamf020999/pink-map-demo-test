"""Mocked browser integration test: route selection + Mapbox response + browser ML.

No external calls are made. This exercises UI code, not live Mapbox's service.
Install: pip install playwright; python -m playwright install chromium
Optional: PINKMAP_CHROMIUM_EXECUTABLE=/usr/bin/chromium python tests/browser_smoke.py
"""
import json
import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

MAPBOX_STUB = '''window.mapboxgl={
 accessToken:null,
 Map:class{constructor(){this.layers=new Set;this.sources=new Set;}
 addControl(){}loaded(){return true;}once(a,fn){fn()}getLayer(n){return this.layers.has(n)}
 getSource(n){return this.sources.has(n)}removeLayer(n){this.layers.delete(n)}
 removeSource(n){this.sources.delete(n)}addSource(n){this.sources.add(n)}
 addLayer(a){this.layers.add(a.id)}setPaintProperty(){}moveLayer(){}fitBounds(){}},
 NavigationControl:class{},GeolocateControl:class{on(){}},
 Marker:class{setLngLat(){return this}setPopup(){return this}addTo(){return this}remove(){}},
 Popup:class{setText(){return this}},LngLatBounds:class{extend(){return this}}
};'''
DRIVING_ROUTES = {'routes': [
 {'distance':12500,'duration':1200,'duration_typical':1300,
  'geometry':{'type':'LineString','coordinates':[[-95.4,29.7],[-95.3,29.8]]}},
 {'distance':14000,'duration':1400,'duration_typical':1390,
  'geometry':{'type':'LineString','coordinates':[[-95.4,29.7],[-95.35,29.75]]}}
]}
WALKING_ROUTES = {'routes': [
 {'distance':1800,'duration':1300,
  'geometry':{'type':'LineString','coordinates':[[-95.4,29.7],[-95.39,29.71]]},
  'legs':[{'steps':[{'maneuver':{'instruction':'Head north on the sidewalk'}},
                      {'maneuver':{'instruction':'Turn right on the path'}}]}]}
]}


def run():
    with sync_playwright() as pw:
        browser_opts={'headless':True,'args':['--no-sandbox']}
        if os.getenv('PINKMAP_CHROMIUM_EXECUTABLE'):
            browser_opts['executable_path']=os.environ['PINKMAP_CHROMIUM_EXECUTABLE']
        browser=pw.chromium.launch(**browser_opts)
        page=browser.new_page(viewport={'width':1200,'height':780})
        errors=[]
        page.on('pageerror',lambda err: errors.append(str(err)))
        seen_requests=[]
        def mocked_directions(req):
            seen_requests.append(req.request.url)
            reply = WALKING_ROUTES if '/walking/' in req.request.url else DRIVING_ROUTES
            req.fulfill(status=200,content_type='application/json',body=json.dumps(reply))
        page.route('https://api.mapbox.com/directions/v5/**', mocked_directions)
        # about:blank blocks localStorage; simulate it for this isolated test only.
        html=(ROOT/'PinkMap_App.html').read_text(encoding='utf-8')
        scripts=re.findall(r'<script>(.*?)</script>',html,re.S)
        assert len(scripts)==1, 'Expected one inline app script'
        page.set_content(re.sub(r'<script[^>]*>.*?</script>','',html,flags=re.S))
        page.add_script_tag(content=MAPBOX_STUB)
        page.add_script_tag(content="""const savedData = new Map();
          Object.defineProperty(window,'localStorage', {configurable:true,value:{
            getItem:k => savedData.has(k) ? savedData.get(k) : null,
            setItem:(k,v) => savedData.set(k,String(v)),
            removeItem:k=>savedData.delete(k)}});""")
        page.add_script_tag(content=(ROOT/'model/traffic_model.js').read_text())
        page.add_script_tag(content=(ROOT/'model/predict.js').read_text())
        page.add_script_tag(content=(ROOT/'model/route_history.js').read_text())
        page.add_script_tag(content=scripts[0])
        assert page.evaluate('Boolean(window.PinkMapAI)'), 'AI model not loaded'
        assert '518 places available' in page.locator('#placeCount').inner_text()
        page.locator('#fromInput').fill('Rice University')
        page.locator('#fromCombo .list .opt').first.click()
        page.locator('#toInput').fill('Hermann Park')
        page.locator('#toCombo .list .opt').first.click()
        page.locator('#go').click()
        page.locator('.ai-estimate').first.wait_for(timeout=4000)
        assert page.locator('#results .card').count()==2
        assert 'AI predicted travel time' in page.locator('.ai-estimate').first.inner_text()
        assert 'Experimental driving AI forecast' in page.locator('#modelInfo').inner_text()
        assert '2 driving route options found' in page.locator('#msg').inner_text()
        assert page.locator('.history-row').count()==1
        assert 'driving-traffic' in seen_requests[-1]
        # Repeated searches train the browser-local frequent-route recommender.
        page.locator('#go').click()
        page.wait_for_function('document.querySelectorAll(".history-row").length === 2')
        assert not page.locator('#suggestions').is_hidden()
        assert '2 searches' in page.locator('#suggestions').inner_text()
        # Walking requests use the pedestrian network, not the driving ML model.
        page.locator('input[name="travelMode"][value="walking"]').check()
        page.locator('#go').click()
        page.wait_for_function('document.querySelectorAll("#results .card").length === 1')
        assert '/mapbox/walking/' in seen_requests[-1]
        assert page.locator('.ai-estimate').count()==0
        assert 'pedestrian route option' in page.locator('#msg').inner_text()
        assert page.locator('.walk-steps').count()==1
        assert page.locator('.history-row').count()==3
        # Repeat a saved driving entry. This restores mode, places and calls the API.
        page.locator('.history-row').last.locator('button').first.click()
        page.wait_for_function('document.querySelectorAll("#results .ai-estimate").length > 0')
        assert 'driving-traffic' in seen_requests[-1]
        assert page.locator('.history-row').count()==4
        # Switching modes clears stale routes.
        page.locator('input[name="travelMode"][value="walking"]').check()
        assert page.locator('#results .card').count()==0
        # Mapbox no-path response must not produce imaginary walking routes or append history.
        page.route('https://api.mapbox.com/directions/v5/mapbox/walking/**',
          lambda req:req.fulfill(status=200,content_type='application/json',body='{"routes":[]}'))
        page.locator('#go').click()
        page.wait_for_function('document.querySelector("#msg").textContent.includes("Could not calculate walking route")')
        assert page.locator('#results .card').count()==0
        assert page.locator('.history-row').count()==4
        page.locator('.history-row').first.locator('button').last.click()
        assert page.locator('.history-row').count()==3
        page.on('dialog', lambda dialog: dialog.accept())
        page.locator('#clearHistory').click()
        assert page.locator('.history-row').count()==0
        assert page.locator('#suggestions').is_hidden()
        if os.getenv('PINKMAP_SMOKE_SCREENSHOT'):
            page.screenshot(path=os.environ['PINKMAP_SMOKE_SCREENSHOT'])
        assert not errors, errors
        print('Mocked browser integration passed: driving, walking, AI, frequent suggestions, save/repeat/delete/clear history, walking error, no JS errors.')
        browser.close()


if __name__=='__main__':run()
