$.domReady(function() {
    var mm = com.modestmaps;

    var map = new mm.Map('map', new wax.mm.connector({
        tiles: [
            'http://a.tiles.mapbox.com/tmcw/1.0.0/tmcw.rrrr2/{z}/{x}/{y}.png',
            'http://b.tiles.mapbox.com/tmcw/1.0.0/tmcw.rrrr2/{z}/{x}/{y}.png',
            'http://c.tiles.mapbox.com/tmcw/1.0.0/tmcw.rrrr2/{z}/{x}/{y}.png',
            'http://d.tiles.mapbox.com/tmcw/1.0.0/tmcw.rrrr2/{z}/{x}/{y}.png'],
        scheme: 'tms'
    }));

    wax.mm.interaction(map, {
        tiles: [
            'http://a.tiles.mapbox.com/tmcw/1.0.0/tmcw.rrrr2/{z}/{x}/{y}.grid.json',
            'http://b.tiles.mapbox.com/tmcw/1.0.0/tmcw.rrrr2/{z}/{x}/{y}.grid.json',
            'http://c.tiles.mapbox.com/tmcw/1.0.0/tmcw.rrrr2/{z}/{x}/{y}.grid.json',
            'http://d.tiles.mapbox.com/tmcw/1.0.0/tmcw.rrrr2/{z}/{x}/{y}.grid.json'],
        scheme: 'tms',
        formatter: function(options, data) {
            if (options.format === 'teaser') {
                if (data.bpm >= 10) {
                    return '<div class="bpm-bar" style="width:' + (data.bpm * 1.5) + 'px;">' + data.bpm + ' <span class="label">bpm</span></div>';
                }
            }
        }
    });

    map.setCenterZoom(new mm.Location(38.92, -77.03), 14);
});
