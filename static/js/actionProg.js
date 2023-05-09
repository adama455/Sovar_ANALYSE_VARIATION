
const tbody = document.getElementById("corps");
const plus = document.getElementById("btn-plus");
var nl = tbody.childNodes.length + 1;

function cre_input(Class, id_input, type, Valeur) {
    input = document.createElement("input");
    input.className = Class;
    input.type = type;
    input.value = Valeur;
    input.setAttribute("id", `${id_input}`);
    input.name = "action";
    // parent.appendChild(input);
    return input;
}

function cre_div(id,content) {
  div = document.createElement("div");
  div.className = "fs-5 py-1 px-2 flex-wrap tx-center tx-dark"
  div.textContent = content
  div.setAttribute("id", `${id}`);
  return div;
}

function cre_td(item) {
    td = document.createElement("td");
    td.className = "border border-dark";
    td.style = "padding: 0 !important;margin: 0 !important";
    td.appendChild(item);
    return td;
}

function cre_td_plus(parent,id) {
  let nbr = tbody.childNodes.length;
  td = document.createElement("td"); 
  td.className ='col-1 d-flex flex-column';
  console.log(parent.childNodes.length);
  i = document.createElement("i");
  i.className = "ri-add-fill text-warning fs-3 btn-plus-tr";
  i.setAttribute("id", id);
  i.style = "cursor:pointer";
  td.appendChild(i);
  parent.appendChild(td);
}

function cre_td_moin(parent,id) {
  i = document.createElement("i");
  i.className = "ri-subtract-fill fs-3 tx-info btn-moin-tr";
  i.setAttribute("id", id);
  i.style = "cursor:pointer";
  parent.appendChild(i);

}

function td_Input(id, type,valeur) {
    return cre_td(cre_input("border-0 w-100 fs-5 py-1 px-2",id, type,valeur))
}

function td_div(id, content) {
    return cre_td(cre_div(id, content))
}

var causes_racines = sessionStorage.getItem('causes_racines').split(',')


//document.getElementById('libelle_act_prog').textContent = causes_racines[0]

for (let index = 0; index <causes_racines.length; index++) { // causes_racines.length = le nbre de causes racine returner
    let nl = tbody.childNodes.length + 1;
    tr = document.createElement("tr");
    tr.className = "";
    tr.setAttribute("id", `line_${nl}`);
    //tr.appendChild(td_div(`cause_${nl}`, "cause rcacine"));
    tr.appendChild(td_Input(`cause_${nl}`,"text", causes_racines[index]));
    cre_td_plus(tr,`btn_plus_tr_${nl}`); //td5
    
    console.log(tr.childNodes.length);
    tbody.appendChild(tr)
    plus_lines = document.querySelectorAll("i.btn-plus-tr");
    console.log(plus_lines.length);
    
    for (let element = 0; element < plus_lines.length; element++) {
        let nac = tbody.childNodes.length;
        let np = tbody.childNodes.length;
        let ne = tbody.childNodes.length;
        plus_lines[element].addEventListener("click", (e) => {
        //console.log(causes_racines)
        e.stopImmediatePropagation();
        plus_ac = document.getElementById(`btn_plus_tr_${nl}`)
        // console.log(plus_ac.parentNode);
        tr = document.getElementById(`line_${nl}`)
        console.log(tr.childNodes.length);
        if(tr.childNodes.length <= 2){
            console.log( e.target.parentNode.parentNode.childNodes.length );
            let t = e.target.parentNode.parentNode.childNodes.length - 1
            let v = e.target.parentNode.parentNode.childNodes.length - 1
            let w = e.target.parentNode.parentNode.childNodes.length - 1
            console.log(e.target.parentNode.previousSibling.nextSibling)

            cre_td_moin(e.target.parentNode,`btn_moin_tr_${nl}`)
            tr.insertBefore(td_Input(`cause_${nl}_action_${t}` ,"text", ""), plus_ac.parentNode)
            tr.insertBefore(td_Input(`cause_${nl}_porteur_${t}` ,"text", ""), plus_ac.parentNode)
            tr.insertBefore(td_Input(`cause_${nl}_echeance${t}` ,"date", ""), plus_ac.parentNode)
        }else{
            td1 = e.target.parentNode.previousSibling.previousSibling.previousSibling;
            let i = td1.childNodes.length + 1;
            td2 = td1.nextSibling;
            let j = td2.childNodes.length + 1;
            td3 = td2.nextSibling;
            let k = td3.childNodes.length + 1;
            console.log(td2);
            // cre_td_moin(e.target.parentNode,`btn_moin_tr_${nl}`)
            td1.appendChild( cre_input("border w-100 fs-5 py-1 px-2", `cause_${nl}_action_${i}`, "text", ""));
            td2.appendChild( cre_input("border w-100 fs-5 py-1 px-2", `cause_${nl}_porteur_${j}`, "text", ""));
            td3.appendChild( cre_input("border w-100 fs-5 py-1 px-2", `cause_${nl}_echeance_${k}`, "date", ""));
        }
        // alert("Okk");
        moin_lines = document.querySelectorAll("i.btn-moin-tr");
        console.log(moin_lines.length);

        for (let elem = 0; elem < moin_lines.length; elem++) {
            moin_lines[elem].addEventListener("click", (e) => { //Supprimer une action
            e.stopImmediatePropagation();
            alert("Salam!!!!!");
            td1 = e.target.parentNode.previousSibling
            td2 = td1.previousSibling
            td3 = td2.previousSibling
            // console.log( td3 = td2.previousSibling);
            if (td1.childNodes.length>1) {
                td1.lastChild.remove()
                td2.lastChild.remove()
                td3.lastChild.remove() 
            }else{
                alert("il faut avoir aumoins deux Aactions!")
            }
            });
        }
        });
    }
    }

function ajax(method, data, Url) {
    var url = new URL(window.location.href);
    //var id_va = url.searchParams.get("id_va");
    //var fichier_id = url.searchParams.get("fichier_id");
    //url = Url +'?fichier_id='+fichier_id+'&id_va='+id_va
    //console.log(url);
    $.ajax({
        data: { data: data }, //grab text between span tags
        type: method,
        url: url, //post grabbed text to flask endpoint for saving role
        async: false,
        success: function (data) {
            //$(".alert-success").css("display", "block");
            //$(".alert-success").append("<h3>Sent Successfully...</h3>");
            console.log("Sent Successfully", url);
        },
        error: function (e) {
            //$(".alert-danger").css("display", "block");
            //$(".alert-danger").append("<h2>Submission failed...</h2>");
            console.log("Submission failed...");
        },
    });
}

$(document).ready(function () {
$("#action_programme").click(function (event) {
    var n = document.getElementById("corps").childNodes;
    var m = document.getElementById("corps").children
    console.log(m);
    var ACTION = [];
    var actions = [];
    n.forEach((element) => { //lines
    console.log("Element",element);
    // for (let j = 0; j < element.childNodes.length; j++) {  //colonnes
        var colonnes = [];
        for (let k = 0; k < element.children[1].childNodes.length; k++) { 
        console.log(element.childNodes[1].childNodes.length);
        colonnes.push(element.children[0].childNodes[0].value);
        console.log("cause===>>",element.children[0].childNodes[0].value);
        colonnes.push(element.children[1].childNodes[k].value);
        colonnes.push(element.children[2].childNodes[k].value);
        colonnes.push(element.children[3].childNodes[k].value);
        //colonnes.push(`code_${element.id}.${k+1}`)
        colonnes.push(`ap${element.id.split('_')[1]}`) // marque(identificateur) de action programme
        console.log(actions);
        colonnes.push('{');
        }
        actions.push(colonnes);
        actions.push('|');

    // }
    });
    ACTION.push(actions);
    console.log(ACTION);
    ajax(
    method= 'POST',
    data = ACTION.toString(),
    url= '9000/sonatel-sovar/analyse/saisi-ap'
    )
    // window.location.reload();
});
});
