#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2020 JR Oakes
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


EXTRACTIONS = {
    'title':            "() => [...document.querySelectorAll('title')].map( el => {return el.textContent;})",
    'description':      "() => [...document.querySelectorAll('meta[name=description]')].map( el => {return el.content;})",
    'h1':               "() => [...document.querySelectorAll('h1')].map( el => {return el.textContent;})",
    'h2':               "() => [...document.querySelectorAll('h2')].map( el => {return el.textContent;})",
    'links':            "() => [...document.querySelectorAll('a')].map( el => {return {'href': el.href, 'text': el.textContent, 'rel':el.rel};})",
    'images':           "() => [...document.querySelectorAll('img')].map( el => {return {'src': el.src, 'alt': el.alt};})",
    'canonical':        "() => [...document.querySelectorAll('link[rel=canonical]')].map( el => {return el.href;})",
    'robots':           "() => [...document.querySelectorAll('meta[name=robots]')].map( el => {return el.content;})",
    'speedMetrics':     "() => return getSpeedMetrics()",
}


WEB_VITALS = """
() => {
    !function(t,e){"object"==typeof exports&&"undefined"!=typeof module?e(exports):"function"==typeof define&&define.amd?define(["exports"],e):e((t=t||self).webVitals={})}(this,(function(t){"use strict";var e,n,i=function(){return"".concat(Date.now(),"-").concat(Math.floor(8999999999999*Math.random())+1e12)},a=function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:-1;return{name:t,value:e,delta:0,entries:[],id:i(),isFinal:!1}},r=function(t,e){try{if(PerformanceObserver.supportedEntryTypes.includes(t)){var n=new PerformanceObserver((function(t){return t.getEntries().map(e)}));return n.observe({type:t,buffered:!0}),n}}catch(t){}},o=!1,s=!1,u=function(t){o=!t.persisted},c=function(){addEventListener("pagehide",u),addEventListener("unload",(function(){}))},d=function(t){var e=arguments.length>1&&void 0!==arguments[1]&&arguments[1];s||(c(),s=!0),addEventListener("visibilitychange",(function(e){var n=e.timeStamp;"hidden"===document.visibilityState&&t({timeStamp:n,isUnloading:o})}),{capture:!0,once:e})},f=function(t,e,n,i){var a;return function(){n&&e.isFinal&&n.disconnect(),e.value>=0&&(i||e.isFinal||"hidden"===document.visibilityState)&&(e.delta=e.value-(a||0),(e.delta||e.isFinal||void 0===a)&&(t(e),a=e.value))}},p=function(){return void 0===e&&(e="hidden"===document.visibilityState?0:1/0,d((function(t){var n=t.timeStamp;return e=n}),!0)),{get timeStamp(){return e}}},l=function(){return n||(n=new Promise((function(t){return["scroll","keydown","pointerdown"].map((function(e){addEventListener(e,t,{once:!0,passive:!0,capture:!0})}))}))),n};t.getCLS=function(t){var e=arguments.length>1&&void 0!==arguments[1]&&arguments[1],n=a("CLS",0),i=function(t){t.hadRecentInput||(n.value+=t.value,n.entries.push(t),s())},o=r("layout-shift",i),s=f(t,n,o,e);d((function(t){var e=t.isUnloading;o&&o.takeRecords().map(i),e&&(n.isFinal=!0),s()}))},t.getFCP=function(t){var e=a("FCP"),n=p(),i=r("paint",(function(t){"first-contentful-paint"===t.name&&t.startTime<n.timeStamp&&(e.value=t.startTime,e.isFinal=!0,e.entries.push(t),o())})),o=f(t,e,i)},t.getFID=function(t){var e=a("FID"),n=p(),i=function(t){t.startTime<n.timeStamp&&(e.value=t.processingStart-t.startTime,e.entries.push(t),e.isFinal=!0,s())},o=r("first-input",i),s=f(t,e,o);d((function(){o&&(o.takeRecords().map(i),o.disconnect())}),!0),o||window.perfMetrics&&window.perfMetrics.onFirstInputDelay&&window.perfMetrics.onFirstInputDelay((function(t,i){i.timeStamp<n.timeStamp&&(e.value=t,e.isFinal=!0,e.entries=[{entryType:"first-input",name:i.type,target:i.target,cancelable:i.cancelable,startTime:i.timeStamp,processingStart:i.timeStamp+t}],s())}))},t.getLCP=function(t){var e=arguments.length>1&&void 0!==arguments[1]&&arguments[1],n=a("LCP"),i=p(),o=function(t){var e=t.startTime;e<i.timeStamp?(n.value=e,n.entries.push(t)):n.isFinal=!0,u()},s=r("largest-contentful-paint",o),u=f(t,n,s,e),c=function(){n.isFinal||(s&&s.takeRecords().map(o),n.isFinal=!0,u())};l().then(c),d(c,!0)},t.getTTFB=function(t){var e,n=a("TTFB");e=function(){try{var e=performance.getEntriesByType("navigation")[0]||function(){var t=performance.timing,e={entryType:"navigation",startTime:0};for(var n in t)"navigationStart"!==n&&"toJSON"!==n&&(e[n]=Math.max(t[n]-t.navigationStart,0));return e}();n.value=n.delta=e.responseStart,n.entries=[e],n.isFinal=!0,t(n)}catch(t){}},"complete"===document.readyState?setTimeout(e,0):addEventListener("pageshow",e)},Object.defineProperty(t,"__esModule",{value:!0})}));

    var getSpeedMetrics = () => {
        const speedMetrics = {};
        for (metric in webVitals){
            webVitals[metric]((result) => {
              speedMetrics[result.name.toLowerCase()] = result.value
            }, true);
        };
        return speedMetrics
    }
}
"""
