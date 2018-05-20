// This file is part of the FlOpEDT/FlOpScheduler project.
// Copyright (c) 2017
// Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
// Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public
// License along with this program. If not, see
// <http://www.gnu.org/licenses/>.
// 
// You can be released from the requirements of the license by purchasing
// a commercial license. Buying such a license is mandatory as soon as
// you develop activities involving the FlOpEDT/FlOpScheduler software
// without disclosing the source code of your own applications.

var margin = {top: 50,  left: 100, right: 10, bot:10};

var svg = {height: 1000 - margin.top - margin.bot, width: 680 - margin.left - margin.right};

var nbPer = 5 ;
var nbSl  = 6 ;

var user = {nom: usna,
	    dispos: [],
	    dispos_bu: []};

var ack = ""; 


/*---------------------
  ------- DISPOS ------
  ---------------------*/
var dispos = [] ;
var par_dispos = {nmax     : 8,
	  	  adv_red  : .7,
		  rad_cross: .6,
		  red_cross: .3
	       };
var smiley = {tete: 13,
	      oeil_x: .35,
	      oeil_y: -.35,
	      oeil_max:.08,
	      oeil_min:.03,
	      bouche_x: .5,
	      bouche_haut_y: -.1,
	      bouche_bas_y: .6,
	      sourcil:.4,
	      init_x:0,
	      init_y:-180,
	      max_r:1,
	      mid_o_v:0xA5*100/255,
	      mid_y_v:0xE0*100/255,
	      min_v:0x90*100/255,
	      rect_w:1.1,
	      rect_h:.3};
var data_dispo_adv_init = [] ;
for (var i = 0 ; i<=par_dispos.nmax ; i++) {
    data_dispo_adv_init.push({
	day:0,
	hour:0,
	off:i
    });
}
var data_dispo_adv_cur = [] ;
var del_dispo_adv = false ;
var dispo_menu_appeared = false ;
/*--------------------
   ------ ALL -------
  --------------------*/

var data_grid_scale_hour = ["8h-9h25","9h30-10h55","11h05-12h30","14h15-15h40","15h45-17h10","17h15-18h40"];
var data_grid_scale_day = ["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI"];

var did = {h: 80, w: 80, mh: 10, mav:5};





create_general_svg();
create_dh_keys();
create_lunchbar();
fetch_dispos();



d3.select("body")
    .on("click", function(d) {
	if(dispo_menu_appeared) {
	    del_dispo_adv = true ;
	    dispo_menu_appeared = false ;
	    go_dispos(true);
	} else {
	    if(del_dispo_adv) {
		del_dispo_adv = false ;
		data_dispo_adv_cur = [] ;
		go_dispos(true);
	    }
	}
    })



function go_dispos(quick) {
    var t, dat, datdi, datsmi ;

    if(quick) {
	t = d3.transition()
	    .duration(0);
    } else {
	t = d3.transition();
    }
    
    dat = mg.selectAll(".dispo")
	.data(user.dispos)
	.attr("cursor","pointer");
	

    datdi = dat
	.enter()
	.append("g")
	.attr("class","dispo");

    var datdisi = datdi
	.append("g")
	.attr("class","dispo-si")
    	.on("click",apply_change_simple_pref);


    
    datdisi
	.append("rect")
	.attr("class","dispo-bg")
	.attr("stroke","black")
	.attr("stroke-width",1)
	.attr("width",dispo_w)
    	.attr("height",0)
	.attr("x",dispo_x)
	.attr("y",dispo_y)
	.attr("fill", function(d){return smi_color(d.val/par_dispos.nmax);})
	.merge(dat.select(".dispo-bg"))
	.transition(t)
	.attr("width",dispo_w)
	.attr("height",dispo_h)
	.attr("x",dispo_x)
	.attr("y",dispo_y)
	.attr("fill",function(d){return smi_color(d.val/par_dispos.nmax);});

    var datex = dat
	.exit();

    datex
	.select(".dispo-bg")
	.transition(t)
	.attr("height",0);
    
    datex
	.remove();


    go_smiley(dat,datdisi,t);

    



    datadvdi = datdi
	.append("g")
	.attr("class","dispo-a");

    datadvdi
	.merge(dat.select(".dispo-a"))
	.on("click",function(d){
	    if(del_dispo_adv) {
		del_dispo_adv = false;
	    }
	    dispo_menu_appeared = true ;
	    data_dispo_adv_cur = data_dispo_adv_init.map(
		function(c) {
		    return {day:d.day, hour:d.hour, off:c.off};
		});
	});
    
    
    datadvdi
	.append("rect")
	.attr("stroke","none")
	.attr("stroke-width",1)
	.attr("fill", "black")
	.attr("opacity",0)
	//.attr("fill", function(d){return smi_color(rc(d));})
	.merge(dat.select(".dispo-a").select("rect"))
	.attr("width",dispo_more_h)
	.attr("height",dispo_more_h)
	.attr("x",dispo_more_x)
	.attr("y",dispo_more_y);
//	.attr("fill", function(d){return smi_color(rc(d));});

    datadvdi
	.append("line")
	.attr("stroke-linecap","butt")
	.attr("stroke","antiquewhite")
	.attr("stroke-width",2)
	.attr("li","h")
	.attr("x1",cross_l_x)
	.attr("y1",cross_m_y)
	.attr("x2",cross_r_x)
	.attr("y2",cross_m_y)
	.merge(dat.select(".dispo-a").select("[li=h]"))
	.transition(t)
	.attr("x1",cross_l_x)
	.attr("y1",cross_m_y)
	.attr("x2",cross_r_x)
	.attr("y2",cross_m_y);

    datadvdi
	.append("line")
	.attr("stroke-linecap","butt")
	.attr("stroke","antiquewhite")
	.attr("stroke-width",2)
	.attr("li","v")
	.attr("x1",cross_m_x)
	.attr("y1",cross_t_y)
	.attr("x2",cross_m_x)
	.attr("y2",cross_d_y)
	.merge(dat.select(".dispo-a").select("[li=v]"))
	.transition(t)
	.attr("x1",cross_m_x)
	.attr("y1",cross_t_y)
	.attr("x2",cross_m_x)
	.attr("y2",cross_d_y);
    
    datadvdi
	.append("circle")
    	.attr("fill","none")
	.attr("stroke","antiquewhite")
	.attr("stroke-width",2)
    	.attr("cx",cross_m_x)
	.attr("cy",cross_m_y)
	.attr("r",par_dispos.rad_cross*smiley.tete)
	.merge(dat.select(".dispo-a").select("circle"))
	.transition(t)
	.attr("cx",cross_m_x)
	.attr("cy",cross_m_y)
	.attr("r",par_dispos.rad_cross*smiley.tete);
    
    

    var dis_men_dat = dg
	.selectAll(".dispo-menu")
	.data(data_dispo_adv_cur);

    var dis_men = dis_men_dat
	.enter()
	.append("g")
	.attr("class","dispo-menu")
	.attr("cursor","pointer")
	.on("click",function(d) {
	    dispos[user.nom][d.day][d.hour]= d.off;
	    user.dispos[day_hour_2_1D(d)].val = d.off});

    dis_men
	.append("rect")
	.attr("class","dis-men-bg")
	.merge(dis_men_dat.select(".dis-men-bg"))
	.transition(t)
	.attr("x",dispo_all_x)
	.attr("y",dispo_all_y)
	.attr("width",dispo_all_w)
	.attr("height",dispo_all_h)
	.attr("fill",function(d){return smi_color(d.off/par_dispos.nmax);})
	.attr("stroke","darkslategrey")
	.attr("stroke-width",2);

    go_smiley(dis_men_dat,dis_men,t);

    
    dis_men_dat.exit().remove();
}


function go_smiley(top, mid, t){
    var datsmi = mid
	.append("g")
	.attr("class","smiley")
	.attr("stroke-width",1)
    	.attr("transform", smile_trans)
	.attr("stroke","black");

    datsmi
	.merge(top.select(".smiley"))
	.transition(t)
    	.attr("transform", smile_trans)
	.attr("stroke","black");

    datsmi
	.append("circle")
	.attr("st","t")
	.merge(top.select("[st=t]"))
	.attr("cx",0)
	.attr("cy",0)
	.attr("r", smiley.tete)
	.attr("stroke",function(d){return tete_str(rc(d));})
	.attr("fill", function(d){return smi_color(rc(d));});

    datsmi
	.append("circle")
	.attr("st","od")
	.attr("fill","none")
	.merge(top.select("[st=od]"))
	.attr("cx",smiley.tete*smiley.oeil_x)
	.attr("cy",smiley.tete*smiley.oeil_y)
	.attr("r",function(d){return oeil_r(rc(d));})
	.attr("stroke-width",function(d){return trait_vis_strw(rc(d));});
    
    datsmi
	.append("circle")
	.attr("st","og")
	.attr("fill","none")
	.merge(top.select("[st=og]"))
	.attr("cx",-smiley.tete*smiley.oeil_x)
	.attr("cy",smiley.tete*smiley.oeil_y)
	.attr("r",function(d){return oeil_r(rc(d));})
	.attr("stroke-width",function(d){return trait_vis_strw(rc(d));});


    datsmi
	.append("line")
	.attr("st","sd")
	.merge(top.select("[st=sd]"))
	.attr("x1",function(d){return sourcil_int_x(rc(d));})
	.attr("y1",function(d){return sourcil_int_y(rc(d));})
	.attr("x2",function(d){return sourcil_ext_x(rc(d));})
	.attr("y2",function(d){return sourcil_ext_y(rc(d));})
	.attr("stroke-width",function(d){return trait_vis_strw(rc(d));});
    
    datsmi
	.append("line")
	.attr("st","sg")
	.merge(top.select("[st=sg]"))
	.attr("x1",function(d){return sourcil_intg_x(rc(d));})
	.attr("y1",function(d){return sourcil_int_y(rc(d));})
	.attr("x2",function(d){return sourcil_extg_x(rc(d));})
	.attr("y2",function(d){return sourcil_ext_y(rc(d));})
	.attr("stroke-width",function(d){return trait_vis_strw(rc(d));});
    
    datsmi
	.append("rect")
	.attr("st","si")
	.merge(top.select("[st=si]"))
	.attr("x",-.5*smiley.rect_w*smiley.tete)
	.attr("y",-.5*smiley.rect_h*smiley.tete)
	.attr("width",function(d){return interdit_w(rc(d));})
	.attr("height",smiley.rect_h*smiley.tete)
	.attr("fill","white")
	.attr("stroke","none");
    
    datsmi
	.append("path")
	.attr("st","b")
	.merge(top.select("[st=b]"))
	.attr("d", function(d){return smile(rc(d));})
	.attr("fill","none")
	.attr("stroke-width",function(d){return trait_vis_strw(rc(d));});


}


function create_lunchbar() {
    fg
	.append("line")
	.attr("class","lunchbar")
	.attr("stroke","black")
	.attr("stroke-width",6)
	.attr("x1",0)
	.attr("y1",gsclb_y)
	.attr("x2",gsclb_x)
	.attr("y2",gsclb_y);

}



/*---------------------
  ------- DISPOS ------
  ---------------------*/
function fetch_dispos() {
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_fetch_stype ,
        async: false,
        contentType: "text/csv",
        success: function (msg) {
	    console.log(msg);
	    
	    console.log("in");

	    dispos[user.nom] = new Array(nbPer);
	    for(var i=0 ; i<nbPer ; i++) {
		dispos[user.nom][i] = new Array(nbSl);
		dispos[user.nom][i].fill(-1);
	    }
	    d3.csvParse(msg, translate_dispos_from_csv);
	    create_dispos_user_data();
	    go_dispos(true);
	    
        },
	error: function(xhr, error) {
	    console.log("error");
	    console.log(xhr);
	    console.log(error);
	    console.log(xhr.responseText);
	    // window.location.href = url_login;
	    //window.location.replace(url_login+"?next="+url_stype);
	}
    });
}


function translate_dispos_from_csv(d) {
    dispos[d.prof][+d.jour][+d.heure] = +d.valeur ;
}




function create_dispos_user_data() {

    var d, j, k;

    user.dispos = [];
    user.dispos_bu = [];

    var current ;

    if (dispos[user.nom]===undefined) {
	console.log("------");
	dispos[user.nom] = new Array(nbPer);
	for(var i=0 ; i<nbPer ; i++) {
	    dispos[user.nom][i] = new Array(nbSl);
	    dispos[user.nom][i].fill(-1);
	}
    }

    
    for(var j = 0 ; j<nbPer ; j++) {
	for(var k = 0 ; k<nbSl ; k++) {
//	    if(!is_free(j,k)) {
	    d2p = { day: j,
		    hour: k,
		    val: dispos[user.nom][j][k],
		    off:-1} ;
	    user.dispos_bu.push(d2p);		
	    if(dispos[user.nom][j][k] < 0) {
		dispos[user.nom][j][k] = par_dispos.nmax;
		console.log(user.nom,j,k);
	    }
	    user.dispos.push({ day: j,
			       hour: k,
			       val:dispos[user.nom][j][k],
			       off:-1});
//	    }
	}
    }

}






function day_hour_2_1D(d){
    return d.day*nbSl+d.hour ;// d.day<4?d.day*nbSl+d.hour:d.day*nbSl+d.hour-3;
}

function dispo_x(d) {
    return d.day*(did.w+did.mh) ;
}
function dispo_y(d) {
    return  d.hour*did.h ;
}
function dispo_w(d){
    return did.w;
}
function dispo_h(d){
    return did.h;
}
function dispo_more_h(d) {
    return .25*did.h ;
}
function dispo_more_y(d) {
    return dispo_y(d) + dispo_h(d) - dispo_more_h(d) ;
}
function dispo_more_x(d) {
    return dispo_x(d) + dispo_w(d) - dispo_more_h(d) ;
}

function dispo_all_x(d) {
    return dispo_more_x(d) + dispo_more_h(d)
	- par_dispos.adv_red*dispo_w(d);
}
function dispo_all_h(d) {
    return 2*did.mav + 2*smiley.tete;
}
function dispo_all_y(d) {
    return dispo_more_y(d) + d.off*dispo_all_h(d);
}
function dispo_all_w(d) {
    return par_dispos.adv_red*dispo_w(d);
}


function cross_l_x(d) {
    return cross_m_x(d) - par_dispos.red_cross*smiley.tete ;
}
function cross_r_x(d) {
    return cross_m_x(d) + par_dispos.red_cross*smiley.tete ;
}
function cross_m_x(d) {
    return dispo_x(d) + dispo_w(d) - 1.7*par_dispos.rad_cross*smiley.tete ;
}
function cross_t_y(d) {
    return cross_m_y(d) - par_dispos.red_cross*smiley.tete ;
}
function cross_m_y(d) {
    return dispo_more_y(d) + .5*dispo_more_h(d) ;
}
function cross_d_y(d) {
    return cross_m_y(d) + par_dispos.red_cross*smiley.tete ;
}



function gsckd_x(datum,i) {
    return  i*(did.w+did.mh)
	+ did.w*.5;
}
function gsckd_y(datum) {
    return  - .25*did.h ;
}
function gsckd_txt(d){
    return d;
}

function gsckh_x(datum) {
    return -did.w ;
}

function gsckh_y(d,i) {
    return  (i+ .5)*did.w;
}
function gsckh_txt(d){
    return d;
}


function gsclb_y()  {
    return did.h*.5*nbSl;
}
function gsclb_x()  {
    return (did.w+did.mh)*nbPer-did.mh;
}

/*---------------------
  ------- SMILEY -------
  ---------------------*/


//ratio content
function rc(d) {
    return d.off==-1?dispos[user.nom][d.day][d.hour]/par_dispos.nmax:d.off/par_dispos.nmax ;
}


function oeil_r(d) {
    return smiley.tete*(smiley.oeil_min+ d*(smiley.oeil_max-smiley.oeil_min));
}
function sourcil_ext_x(d) {
    return smiley.tete*(smiley.oeil_x + d*smiley.sourcil);
}
function sourcil_int_x(d) {
    return smiley.tete*(smiley.oeil_x - (1-d)*smiley.sourcil);
}
function sourcil_ext_y(d) {
    return smiley.tete*(smiley.oeil_y - (1-d)*smiley.sourcil);
}
function sourcil_int_y(d) {
    return smiley.tete*(smiley.oeil_y - d*smiley.sourcil);
}
function sourcil_extg_x(d) {
    return -smiley.tete*((smiley.oeil_x + d*smiley.sourcil));
}
function sourcil_intg_x(d) {
    return -smiley.tete*((smiley.oeil_x - (1-d)*smiley.sourcil));
}
function smile(d){
    return "M" +
	(-smiley.tete*smiley.bouche_x) +" "+ smile_coin_y(d) +" Q0 "+
	(smiley.tete*(2*smiley.bouche_haut_y-smiley.bouche_bas_y
		      + 3*d*(smiley.bouche_bas_y-smiley.bouche_haut_y))) + " " +
	(smiley.tete*smiley.bouche_x) +" "+ smile_coin_y(d) ;
}
    
    
function smile_coin_y(d){
    return smiley.tete*(smiley.bouche_bas_y
			+ d*(smiley.bouche_haut_y-smiley.bouche_bas_y));
}

function smi_color(d) {
    if(d<=.5) {
	return "rgb("+
	    100+"%,"+
	    2*d*smiley.mid_o_v+"%,"+
	    0+"%)";
    } else {
	return "rgb("+
	    200*(1-d)+"%,"+
	    ((smiley.min_v-smiley.mid_y_v)*(-1+2*d)+smiley.mid_y_v)+"%,"+
	    0+"%)";
    }
}

function tete_str(d) {
    return d==0?"white":"black";
}
function trait_vis_strw(d) {
    return d==0?0:1;
}
function interdit_w(d) {
    return d==0?smiley.rect_w*smiley.tete:0;
}

function smile_trans(d) {
    if(d.off==-1){
	return "translate("+
	(dispo_x(d)+.5*did.w) + "," +
	    (dispo_y(d)+.5*did.h) + ")";
    } else {
	return "translate("+
	    (dispo_x(d)+(1-.5*par_dispos.adv_red)*dispo_w(d)) + "," +
	    (dispo_all_y(d)+smiley.tete+did.mav) + ")";
    }
}


function apply_change_simple_pref(d){
    if(Math.floor(d.val%(par_dispos.nmax/2))!=0) {
	d.val = Math.floor(d.val/(par_dispos.nmax/2))*par_dispos.nmax/2;
    }
    d.val = (d.val+par_dispos.nmax/2)%(3*par_dispos.nmax/2);
    dispos[user.nom][d.day][d.hour]=d.val;
    user.dispos[day_hour_2_1D(d)].val = d.val;
    go_dispos(true);
}






/*
function is_free(day,hour) {
    return (day==3 && hour>2);
}
*/




function create_general_svg() {
    svg_cont = d3.select("body").select("[id=\"svg\"]").append("svg")
	.attr("width",svg.width)
	.attr("height",svg.height)
	.attr("text-anchor","middle")
//	.attr("dominant-baseline","central")
//	.attr("alignment-baseline","middle")
//	.attr("font-family","Open Symbol")
//	.attr("font-size",12)
	.append("g")
	.attr("transform","translate("+margin.left + "," + margin.top + ")");

    create_layouts(svg_cont);
}


function create_layouts(svg_cont){


    // valider
    vg = svg_cont.append("g")
	.attr("id","lay-vg");
    
    // background, middleground, foreground, dragground
    mg = svg_cont.append("g")
	.attr("id","lay-mg");
    fg = svg_cont.append("g")
	.attr("id","lay-fg");
    dg = svg_cont.append("g")
	.attr("id","lay-dg");


    
}



function create_dh_keys() {
    fg
	.selectAll(".gridsckd")
	.data(data_grid_scale_day)
	.enter()
	.append("text")
	.attr("class","gridsckd")
	.attr("x",gsckd_x)
	.attr("y",gsckd_y)
	.attr("font-size",13)
	.attr("font-weight","bold")
	.text(gsckd_txt);

    fg
	.selectAll(".gridsckh")
	.data(data_grid_scale_hour)
	.enter()
	.append("text")
	.attr("class","gridsckh")
	.attr("x",gsckh_x)
	.attr("y",gsckh_y)
	.text(gsckh_txt);
    

}





function rearrange_dispos(save) {
    var changes = [] ;
    var i =0;
    
    for(var j = 0 ; j<nbPer ; j++) {
	for(var k = 0 ; k<nbSl ; k++) {
//	    if(!is_free(j,k)) {
		if(!save ||
		   user.dispos[i].val != user.dispos_bu[i].val) {
		    changes.push({ day: j, hour: k, val:user.dispos[i].val});
		}
		i+=1;
	    }
//	}
    }

    user.dispos_bu = user.dispos.slice(0);

    return changes ;
}

function writeNext(i)
{
    document.write(i);

    if(i == 5)
        return;

    setTimeout(function()
    {
        writeNext(i + 1);

    }, 2000);
}



function apply_stype(save) {
    console.log("app");
    console.log(document.forms['app']);
    console.log();
    var changes = rearrange_dispos();

    var se_deb,an_deb,se_fin,an_fin;
    var an, se;
    var se_abs_max = 53;
    var se_min, se_max;

    if(save){
	se_deb = 0 ;
	console.log(annee_courante);
	an_deb = +annee_courante ;
	se_fin = se_deb ;
	an_fin = an_deb ;
    } else {
	se_deb = +document.forms['app'].elements['se_deb'].value ;
	an_deb = +document.forms['app'].elements['an_deb'].value ;
	se_fin = +document.forms['app'].elements['se_fin'].value ;
	an_fin = +document.forms['app'].elements['an_fin'].value ;
    }


    if (an_deb<an_fin ||
        (an_deb==an_fin && se_deb<=se_fin)){

    //user.
    
    // console.log(changes);
    // console.log(JSON.stringify({create: create, tab: changes}));
    // console.log(JSON.stringify(changes));


	if(changes.length==0) {
    	    ack = "RAS";
	} else {

	    for (an=an_deb ; an<=an_fin ; an++){
		if(an==an_deb){
		    se_min = se_deb;
		} else {
		    se_min = 1;
		}
		if(an==an_fin){
		    se_max = se_fin;
		} else {
		    se_max = se_abs_max;
		}
		
		for (se=se_min ; se<=se_max ; se++) {
		    //console.log(se,an);
    		    $.ajax({
    			url: url_dispos_changes
			    + "?s=" + se
			    + "&a=" + an
			    + "&u=" + user.nom,
			type: 'POST',
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify(changes),
			dataType: 'json',
    			success: function(msg) {

    			},
    			error: function(msg){

    			}
    		    });
		}
		//writeNext(1);		
	    }
	    ack = "Ok ";
	    if(save){
		ack += "semaine type";
	    } else {
		ack += "semaine "+se_deb+" année "+an_deb
		    +" à semaine "+se_fin+" année "+an_fin;
	    }
	}

    } else {
	ack = "Problème : seconde semaine avant la première";
    }

    document.getElementById("ack").textContent = ack ;
//   writeNext(1);    
     
}
