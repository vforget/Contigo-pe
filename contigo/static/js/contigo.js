CONTIGO.float_precision = 4;
CONTIGO.contigs = [];

var stats = {};

function xy_chart(x_cat, y_cat) {
    //  Plots XY-Chart: 
    //  - Allowed axis are specified in pulldown menus of HTML
    //  - Ranges are REQUIRED and are specified in assembly.js
    //	  - Data points are specified in assembly.js
    //	  - Axis transforms and tick_labels are OPTIONALLY specified in assembly.js.
    
    
    var d1 = [];
    var i = 0;
    
    // Get ranges, REQUIRED!
    
    var min_x = CONTIGO.ranges.min[x_cat];
    var max_x = CONTIGO.ranges.max[x_cat];
    var min_y = CONTIGO.ranges.min[y_cat];
    var max_y = CONTIGO.ranges.max[y_cat];
    
    
    // Optionally, transform data range to log
    if (CONTIGO.is_log[x_cat]) {
	min_x = Math.log(min_x)/Math.LN10;
	max_x = Math.log(max_x)/Math.LN10;
    }
    if (CONTIGO.is_log[y_cat]) {
	min_y = Math.log(min_y)/Math.LN10;
	max_y = Math.log(max_y)/Math.LN10;
    }
    
    // Round off data ranges
    min_x = Math.floor(min_x);
    min_y = Math.floor(min_y);
    max_x = Math.ceil(max_x);
    max_y = Math.ceil(max_y);
    
    // Set x tick labels
    var x_axis = { min: min_x, max: max_x, ticks: null };
    
    // If log x or y axis, push tick custom labels
    var x_ticks = [];
    if (CONTIGO.is_log[x_cat]){
	for (i = min_x; i <= max_x; i += 1){
            x_ticks.push([i,CONTIGO.tick_labels[x_cat][i]]);
	}
	x_axis.ticks = x_ticks;
    }
    
    var y_axis = { min: min_y, max: max_y, ticks: null };
    var y_ticks = [];
    
    if (CONTIGO.is_log[y_cat]){
	for (i = min_y; i <= max_y; i += 1){
            y_ticks.push([i,CONTIGO.tick_labels[y_cat][i]]);
	}
	y_axis.ticks = y_ticks;
    }    
    
    // Get data points
    var x_val = null;
    var y_val = null;
    
    var num_points = CONTIGO.contigs.length;
    for (i = 0; i < num_points; i += 1) {
	var ctg = CONTIGO.contigs[i];
	if (!ctg) {
	    alert(ctg);
	}
	x_val = CONTIGO.assembly[ctg][x_cat];
        y_val = CONTIGO.assembly[ctg][y_cat];
        if (CONTIGO.is_log[x_cat]) {
            x_val = Math.log(CONTIGO.assembly[ctg][x_cat])/Math.LN10;
            
        }

        
        if (CONTIGO.is_log[y_cat]) {
            y_val = Math.log(CONTIGO.assembly[ctg][y_cat])/Math.LN10;
            
        }
        d1.push([x_val, y_val]);
    }
    
    // plot options
    var options = { xaxis: x_axis,                         
                    yaxis: y_axis,
                    colors: ["#000"],
		    grid: { color: "#000",
			    backgroundColor: "#fff",
			    borderWidth: 1,
			    tickColor: "#ccc",
			    clickable: true,
			    autoHighlight: true },
		    selection: { mode: "xy", color: '#f00' }
		    
    };
    
    $.plot($("#xy_chart"), [{ data: d1, 
		    points: { show: true, radius: 0.3},
		    shadowSize: 1,
		    colors: ["#000"]
		    }], options);
    
}

$("#xy_chart").bind("plotclick", function (event, pos, item) {
	    var x_cat = $('#xy_chart_x').val();
	    var y_cat = $('#xy_chart_y').val();
	    var x_txt = $('#xy_chart_x :selected').text();
	    var y_txt = $('#xy_chart_y :selected').text();
	    if (item) {
		x_val = item.datapoint[0];
		y_val = item.datapoint[1];
		if (CONTIGO.is_log[x_cat]){
		    x_val = Math.pow(10, x_val);
		} 
		if (CONTIGO.is_log[y_cat]){
		    y_val = Math.pow(10, y_val);
		} 
		x_val = Math.round(x_val);
		y_val = Math.round(y_val);
		var ctg = CONTIGO.contigs[item.dataIndex];
		$("#xy_chart_detail").html(CONTIGO.assembly[ctg].name + ": " + CONTIGO.assembly[ctg].length + "nt, " + CONTIGO.assembly[ctg].avg_depth + "x, " + CONTIGO.assembly[ctg].avg_gc + "%GC");
		
	    }
	
	});
    
    
    $("#xy_chart").bind("plotselected", function(event, ranges) {
	    var x_cat = $('#xy_chart_x').val();
	    var y_cat = $('#xy_chart_y').val();
	    var x_txt = $('#xy_chart_x :selected').text();
	    var y_txt = $('#xy_chart_y :selected').text();
	    
	    var x1_val = ranges.xaxis.from;
	    var x2_val = ranges.xaxis.to;
	    var y1_val = ranges.yaxis.from;
	    var y2_val = ranges.yaxis.to;
	    
	    if (CONTIGO.is_log[x_cat]){
		x1_val = Math.pow(10, x1_val);
		x2_val = Math.pow(10, x2_val);
	    } 
	    if (CONTIGO.is_log[y_cat]){
		y1_val = Math.pow(10, y1_val);
		y2_val = Math.pow(10, y2_val);
	    } 
	    x1_val = Math.round(x1_val);
	    y1_val = Math.round(y1_val);
	    x2_val = Math.round(x2_val);
	    y2_val = Math.round(y2_val);
	    
	    var x_stat = 0.0;
	    var y_stat = 0.0;
	    var c = 0.0;
	    
	    var num_points = CONTIGO.contigs.length;
	    for (i = 0; i < num_points; i += 1) {
		var ctg = CONTIGO.contigs[i];
		x_val = CONTIGO.assembly[ctg][x_cat];
		y_val = CONTIGO.assembly[ctg][y_cat];
		if ((x_val >= x1_val) && (x_val <= x2_val) &&
		    (y_val >= y1_val) && (y_val <= y2_val))
		    {
			c += 1;
			x_stat += x_val;
			y_stat += y_val;
		    }
	    }
	    
	    var y_avg = (y_stat / c).toFixed(2);
	    var x_avg = (x_stat / c).toFixed(2);
	    
	    
	    title = "Statistics";
	    var w = window.open('','Statistics','width=700,height=700,menubar=0,toolbar=0,status=0,scrollbars=1,resizable=1');
	    w.document.writeln('<html><head><title>'+ title +'</title></head>' +
			       '<body onLoad="self.focus()" style="background-color: #FFF; color: #000;">');
	    w.document.writeln(c + " " + x_txt + " " + x1_val + " " + x2_val + " " + (x2_val-x1_val) + " " + 
			       " " + x_stat + " " + x_avg + " " +
			       y_txt + " " + y1_val + " " + y2_val + " " + (y2_val-y1_val) + " " +
			       " " + y_stat + " " + y_avg + " " +
			       "</br>");
	    w.document.writeln('</body></html>');
	    
	});
    
	
	
function m_chart(cat){
       
    var d = [];
    var min = CONTIGO.ranges.min[cat];
    var max = CONTIGO.ranges.max[cat];
    var i = 0;
    //$("#m_chart_detail").html("<span class=\"help\">Click point to get approx value</span>");
    if (CONTIGO.is_log[cat]) {
       min = Math.log(min)/Math.LN10;
       max = Math.log(max)/Math.LN10;
    }
    min = Math.floor(min);
    max = Math.ceil(max);
    var x_axis = { min: min,
		   max: max,
		   ticks: null
             };
    var ticks = [];
    if (CONTIGO.is_log[cat]){
       for (i = min; i <= max; i += 1){
           ticks.push([i,CONTIGO.tick_labels[cat][i]]);
       }
       x_axis.ticks = ticks;
    }

    var total_length = 0;
    var num_points = CONTIGO.contigs.length;
    for (i = 0; i < num_points; i += 1) {
	var ctg = CONTIGO.contigs[i];
	d.push([CONTIGO.assembly[ctg].length, CONTIGO.assembly[ctg][cat]]);
	total_length += CONTIGO.assembly[ctg].length;
    }
    d.sort(function(a,b){return b[1] - a[1];});
    var sum = 0;
    var d2 = [];
    var x_val = null;
    var y_val = null;
    var x_95 = 0;
    for (i = 0; i < (d.length); i += 1) {
        sum += d[i][0];
        x_val = d[i][1];
        y_val = (sum/total_length) * 100;
        if (CONTIGO.is_log[cat]){
           x_val = Math.log(d[i][1])/Math.LN10;
        }
        if (y_val < 95){
	    x_95 = x_val;
	}
        d2.push([x_val, y_val]);
    }
    var options = { xaxis: x_axis,
                    colors: ["#000"],
                    selection: {
                                 mode: "xy",
                                 color: "#f00"
	                       },
                    grid: {
	                   color: "#000",
                           backgroundColor: "#fff",
                           borderWidth: 1,
                           tickColor: "#ccc",
                           clickable: true,
                           autoHighlight: true,
			   markings: [ { yaxis: { from: 50, to: 50 }, color: "#ff0000" } ]

 
		    }
		    

    };
    
    $.plot($("#m_chart"), [{ data: d2, 
                    lines: { show: true },
		    points: { show: false, radius: 0.5 },
		    shadowSize: 0,
		    colors: ["#000"],
		    fillColor: ["#000"]
		    }                              
	    ],
	options
                          
      );
   
}

$("#m_chart").bind("plotclick", function (event, pos, item) {
    var cat = $('#m_chart_cat').val();
    var txt = $('#m_chart_cat :selected').text();
    if (item) {
	x_val = item.datapoint[0];
	y_val = item.datapoint[1];
	if (CONTIGO.is_log[cat]){
	    x_val = Math.pow(10, x_val);
	}
	x_val = Math.round(x_val);
	y_val = y_val.toFixed(2);
	$("#m_chart_detail").html(y_val + "% with " + txt + " >= " + x_val);
    }
});

$("#m_chart").bind("plotselected", function(event, ranges) {
	var x_cat = $('#m_chart_cat').val();
	var x_txt = $('#m_chart_cat :selected').text();
	var y_txt = "Percent";
	
	var x1_val = ranges.xaxis.from;
	var x2_val = ranges.xaxis.to;
	var y1_val = ranges.yaxis.from;
	var y2_val = ranges.yaxis.to;
	
	if (CONTIGO.is_log[x_cat]){
	    x1_val = Math.pow(10, x1_val);
	    x2_val = Math.pow(10, x2_val);
	} 
	x1_val = Math.round(x1_val);
	y1_val = Math.round(y1_val);
	x2_val = Math.round(x2_val);
	y2_val = Math.round(y2_val);
	
	alert(x_txt + ": " + x1_val + "-" + x2_val + " (" + (x2_val-x1_val) + "), " + y_txt + ": " + y1_val + "-" + y2_val + " (" + (y2_val-y1_val) + ")");
    	
    });


function h_chart(cat) {
    /*
      Plots Histogram 
    */
    
    var d3 = [];
    var sum = 0;
    var min = CONTIGO.ranges.min[cat];
    var max = CONTIGO.ranges.max[cat];
    var i = 0;
    //$("#h_chart_detail").html("<span class=\"help\">Click point to get approx value</span>");
    if (CONTIGO.is_log[cat]) {
	min = Math.log(min)/Math.LN10;
	max = Math.log(max)/Math.LN10;
    }
    min = Math.floor(min);
    max = Math.ceil(max);
    var x_axis = { min: min,
		   max: max,
		   ticks: null
             };
    var ticks = [];
    if (CONTIGO.is_log[cat]){
       for (i = min; i <= max; i += 1){
           ticks.push([i,CONTIGO.tick_labels[cat][i]]);
       }
       x_axis.ticks = ticks;
    }
    for (i = 0; i < CONTIGO.hist_data[cat].length; i += 1) {
	sum += CONTIGO.hist_data[cat][i];
    }
    var y_min = 1;
    var y_max = 0;
    for (i = 0; i < CONTIGO.hist_data[cat].length; i += 1) {
	y_val = CONTIGO.hist_data[cat][i];
	if (y_val > 0){
	    
	    x_val = i;
	    if (CONTIGO.is_log[cat]){
		x_val = Math.log(x_val)/Math.LN10;
	    }
	    y_val = Math.log(y_val)/Math.LN10;
	    if (y_val == -Infinity) {
		y_val = 0;
	    }
	    if (x_val == -Infinity) {
		x_val = 0;
	    }
	    if (y_val > y_max) {
		y_max = y_val;
	    }
	    if (y_val < y_min) {
		y_min = y_val;
	    }
	    d3.push([x_val, y_val]);
	}
	
    }
    y_min = Math.floor(y_min);
    y_max = Math.ceil(y_max);
    var y_axis = { min: y_min,
		   max: y_max,
		   ticks: null
             };
    
    ticks = [];
    for (i = y_min; i <= y_max; i += 1){
        ticks.push([i,Math.pow(10,i)]);
	
    }
    y_axis.ticks = ticks;
    
    var options = { xaxis: x_axis,
		    yaxis: y_axis,
                    colors: ["#000"],
                    selection: {
 	              mode: "xy",
 	              color: "#f00"
	            },
                    grid: {
                        color: "#000",
                        backgroundColor: "#fff",
			borderWidth: 1,
                        tickColor: "#ccc",
                        clickable: true,
			autoHighlight: true
                    }
                  };
    
    $.plot($("#h_chart"), [{ data: d3,
                    lines: { show: true },
		    points: { show: false, radius: 0.5 },
		    shadowSize: 0,
		    colors: ["#000"],
		    fillColor: ["#000"]
		    }                              
	    ],
	options
	);
}

$("#h_chart").bind("plotclick", function (event, pos, item) {
    var cat = $('#h_chart_cat').val();
    var txt = $('#h_chart_cat :selected').text();
    var x_val = null;
    var y_val = null;
    if (item) {
	x_val = item.datapoint[0];
	y_val = item.datapoint[1];
	if (CONTIGO.is_log[cat]){
	    x_val = Math.pow(10, x_val);
	}
	
	x_val = Math.round(x_val);
	y_val = Math.pow(10,y_val).toFixed(0);
	$("#h_chart_detail").html(y_val + " with " + txt + " = " + x_val);
    }
});



$("#h_chart").bind("plotselected", function(event, ranges) {
    var x_cat = $('#h_chart_cat').val();
    var x_txt = $('#h_chart_cat :selected').text();
    var y_txt = "Counts";
    
    var x1_val = ranges.xaxis.from;
    var x2_val = ranges.xaxis.to;
    var y1_val = ranges.yaxis.from;
    var y2_val = ranges.yaxis.to;
    var y_sum = 0;
    var sum = 0;
    var perc = 0.0;
    
    if (CONTIGO.is_log[x_cat]){
	x1_val = Math.pow(10, x1_val);
	x2_val = Math.pow(10, x2_val);
    }
    x1_val = Math.round(x1_val);
    x2_val = Math.round(x2_val);
    y1_val = Math.pow(10,y1_val).toFixed(0);
    y2_val = Math.pow(10,y2_val).toFixed(0);
    for (i = 1; i < CONTIGO.hist_data[x_cat].length; i += 1) {
	sum += CONTIGO.hist_data[x_cat][i];
	    if ((i >= x1_val) && (i <= x2_val) && (CONTIGO.hist_data[x_cat][i] >= y1_val) && (CONTIGO.hist_data[x_cat][i] <= y2_val)){
		y_sum += CONTIGO.hist_data[x_cat][i];
	    }
    }
    
    perc = ((y_sum/sum)*100).toFixed(2);
    alert(y_sum + " (" + perc + "%) w/ " + x_txt + " from " + x1_val + "-" + x2_val + " and " + y_txt + " from " + y1_val + "-" + y2_val);
    
});

$("#filter").click(function(){
        var val = null;
	val = $("#filter1select").val(); 
	var scaff_name = null;
	CONTIGO.contigs = [];
	if (val == 'all scaffolds'){			
	    for (scaff_name in CONTIGO.scaffolds) {
		CONTIGO.contigs = CONTIGO.contigs.concat(CONTIGO.scaffolds[scaff_name].contigs);
	    }
	} else if (val.substring(0, 8) == 'scaffold'){
	    CONTIGO.contigs = CONTIGO.scaffolds[val].contigs;
	} else if (val.substring(0, 6) == 'contig'){
	    CONTIGO.contigs = [val];
	} else {
	    alert("Invalid option in filter select");
	}
	$('#num_filter_pt').html(CONTIGO.contigs.length);
	$('#filter_item').html(val);
	xy_chart($('#xy_chart_x').val(), $('#xy_chart_y').val());
	m_chart($('#m_chart_cat').val());
	h_chart($('#h_chart_cat').val());
    });