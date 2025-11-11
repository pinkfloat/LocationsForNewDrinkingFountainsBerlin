const stations = require('vbb-stations')
const lines = require('vbb-osm-relations/lines')
const platforms = require('vbb-osm-relations/platforms.json')
const entrances = require('vbb-osm-relations/entrances.json')

// Einzelne Station abrufen
const station = stations('de:11000:900009101')
console.log('Station U Amrumer Str.:', station)

// Stationen nach Filter
const filtered = stations({ weight: 2474, 'location.latitude': 52.542202 })
console.log('Gefilterte Stationen:', filtered)

// Funktion / Keys des Stations-Moduls
console.log('Stations keys (function properties):', Object.keys(stations))

// Lines
console.log('Beispiel: Lines.U7 =', lines.U7)
console.log('10 Linien:', Object.keys(lines).slice(0,10)) // erste 10 Lines

// Platforms
console.log('Platforms keys (erste 10):', Object.keys(platforms).slice(0,10))
console.log('Plattformen für 900000056104 (U Bülowstr.):', platforms['900000056104'])

// Entrances
console.log('Entrances keys (erste 10):', Object.keys(entrances).slice(0,10))
console.log('Eingänge für 900000130011 (U Vinetastr.):', entrances['900000130011'])

// Ganze Objekte inspecten (komplett, falls nötig)
// console.log(util.inspect(platforms, { depth: 2, colors: true, maxArrayLength: 20 }))
// console.log(util.inspect(entrances, { depth: 2, colors: true, maxArrayLength: 20 }))
