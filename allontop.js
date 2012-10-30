var Canvas = require('canvas'),
    fs = require('fs');

var w = 1024, h = 768;
var c = new Canvas(w, h);
var ctx = c.getContext('2d');

ctx.fillStyle = '#000';
ctx.fillRect(0, 0, w, h);
ctx.strokeStyle = '#000';
ctx.lineWidth = 1;
ctx.globalAlpha = 0.9;
ctx.globalCompositeOperation = 'screen';

var runs = JSON.parse(fs.readFileSync('lines.geojson'));

function xscale(coords, off) {
    var xes = coords.map(function(c) { return c[0]; });
    var min = Math.min.apply(Math, xes);
    var max = Math.max.apply(Math, xes);
    return function(x) {
        return (((x - min) / (max - min)) * w) + off;
    };
}

function yscale(coords, off) {
    var xes = coords.map(function(c) { return c[1]; });
    var min = Math.min.apply(Math, xes);
    var max = Math.max.apply(Math, xes);
    return function(x) {
        return (((x - min) / (max - min)) * h) + off;
    };
}

var offx = 0, offy = 0;
for (var i = 0; i < runs.features.length; i++) {
    if (i % 3 === 0) ctx.strokeStyle = '#22ffff';
    if (i % 3 === 1) ctx.strokeStyle = '#ff22ff';
    if (i % 3 === 2) ctx.strokeStyle = '#00FF99';
    var run = runs.features[i].geometry.coordinates;
    var xs = xscale(run, offx);
    var ys = yscale(run, offy);
    ctx.beginPath();
    ctx.moveTo(xs(run[0][0]), ys(run[0][1]));
    for (var j = 1; j < run.length; j++) {
        ctx.lineTo(xs(run[j][0]), ys(run[j][1]));
    }
    ctx.stroke();
}

fs.writeFileSync('allontop.png', c.toBuffer());
