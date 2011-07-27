$.domReady(function() {
    var mm = com.modestmaps;

    var map = new mm.Map('map', new wax.mm.connector({
        tiles: ['http://localhost:8889/1.0.0/running_map/{z}/{x}/{y}.png?1311763836000'],
        scheme: 'tms'
    }));

    wax.mm.interaction(map, {
        grids: ['http://localhost:8889/1.0.0/running_map/{z}/{x}/{y}.grid.json?1311763836000'],
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
