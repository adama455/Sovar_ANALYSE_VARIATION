
const form_actions = document.getElementById("form_actions");
const form_input = document.getElementById("form-input");
const recap_action = document.getElementById("recaputilatif");
const array = [];
var numero //numero du button cliquer..........

var liste_labelle = [
  "Libelle Action",
  "Porteur",
  "Echeance",
];
var liste_id = [
  "libelle_action",
  "porteur_action",
  "echeance_action",
];
var data_acton = [];
  
function sous_bloc_action(parent, n, i, id, label) {
  const div_ref = document.createElement("div");
  div_ref.className = "col-3 d-flex flex-column";
  label_ref = document.createElement("label");
  label_ref.for = `${id}_${n}.${i}`;
  label_ref.className = "d-flex justify-content-start";
  label_ref.innerHTML = label;
  input_ref = document.createElement("input");
  input_ref.className = "fs-5 ps-2";
  input_ref.id = `${id}_${n}.${i}`;
  // console.log(input_ref.id);
  input_ref.name = `${id}_${n}.${i}`;
  if (label == "Libelle Action") {
    div_ref.className = "col-6 d-flex flex-column";
  }
  if (label == "Porteur") {
    div_ref.className = "col-3 d-flex flex-column";
  }
  if (label == "Echeance") {
    input_ref.type = "date";
    div_ref.className = "col-3 d-flex flex-column";
  }

  div_ref.appendChild(label_ref);
  div_ref.appendChild(input_ref);
  parent.appendChild(div_ref);
}
  
function bloc_actions(parent, n) {
  var i = form_input.childNodes.length;
  //const H3 = document.createElement("h3");
  //H3.innerHTML = `Action_n°${i}`;
  //H3.className = "modal-title fs-5 py-2";
  const row = document.createElement("div");
  row.className = "row mb-3 ";
  row.id = `row_action_${n}`;
  //row.append(H3);
  for (let index = 0; index < 3; index++) {
    sous_bloc_action(row, n, i, liste_id[index], liste_labelle[index]);
  }
  parent.appendChild(row);
}    

//////Récuperer le dernier Pourquoi.......///////////
    
function le_dernier_cause(numero,tmp){
    for (let i = 1; i < 7; i++) {
      if (numero == i){
        if(document.getElementById(`input_5${i}`).value != ""){
          tmp = document.getElementById(`input_5${i}`).value
        }else if(document.getElementById(`input_4${i}`).value != ""){
          tmp = document.getElementById(`input_4${i}`).value
        }else if(document.getElementById(`input_3${i}`).value != ""){
          tmp = document.getElementById(`input_3${i}`).value
        }else if(document.getElementById(`input_2${i}`).value != ""){
          tmp = document.getElementById(`input_2${i}`).value
        }
      }
    }
    console.log("dernier_pourquoi========>", tmp)
    return tmp;
}

const def= document.querySelectorAll(".definir_action")
def.forEach((element) => {
  //$(element).on('click', function () {
  element.addEventListener('click', ()=>{
    var k = element.getAttribute('id').split('_').pop()
    console.log(k);
    numero = k  //numero du button cliquer..........
    alert("Click")
    $('#modal_action').modal('show');
    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
      bloc_actions(form_input, k);
      document.getElementById("autre-act").addEventListener('click', ()=>{
        alert("SAlam::Click")
        bloc_actions(form_input, k);
      })
    })

    // //////Récuperer le dernier Pourquoi.......///////////
    
    // function le_dernier_cause(numero,tmp){
    //   for (let i = 1; i < 7; i++) {
    //     if (numero == i){
    //       if(document.getElementById(`input_5${i}`).value != ""){
    //         tmp = document.getElementById(`input_5${i}`).value
    //       }else if(document.getElementById(`input_4${i}`).value != ""){
    //         tmp = document.getElementById(`input_4${i}`).value
    //       }else if(document.getElementById(`input_3${i}`).value != ""){
    //         tmp = document.getElementById(`input_3${i}`).value
    //       }else if(document.getElementById(`input_2${i}`).value != ""){
    //         tmp = document.getElementById(`input_2${i}`).value
    //       }
    //     }
    //   }
    //   console.log("dernier_pourquoi========>", tmp)
    //   return tmp;
    // }
    
    //le_dernier_pourquoi(numero,dernier_pourquoi)
    var dernier_pourquoi;
    document.getElementById("dernier-pourquoi").innerHTML = le_dernier_cause(numero,dernier_pourquoi)
  })
})

function ajax(method, data, Url) {
  var url = new URL(window.location.href);
  //var id = document.getElementById("identifiant_act").value;
  //console.log(id);
  //var reference = document.getElementById("reference_av_act").value;
  //var id_va = url.searchParams.get("id_va");
  //var fichier_id = url.searchParams.get("fichier_id");
  //url = Url +'?fichier_id='+fichier_id+'&id_va='+id_va
  //console.log(url)
  $.ajax({
    data: { data: data }, //grab text between span tags
    type: method,
    url: url, //post grabbed text to flask endpoint for saving role
    async: false,
    success: function (data) {
      console.log("Sent Successfully", url);
    },
    error: function (e) {
      console.log("Submission failed...");
    },
  });
}

var ACTION = [];
var test = ["encore testons"];
var valider = document.getElementById("bouton_valider_action")
var cause_racine
// var cause = document.getElementById("dernier-pourquoi").textContent
// console.log("causecausecause",cause);
//valider.addEventListener("click", (e)=>{    
  // event.preventDefault();
  $(document).ready(function () {
    $("#bouton_valider_action").click(function (event) {
      //alert("kong testons")
      var nbre = document.getElementById("form-input").childNodes;
      for (let i = 1; i < nbre.length; i++) {  //pour chaque row
        var action = [];
        for (let j = 0; j < nbre[i].childNodes.length; j++) {  //chaque bloc input d'une row
        //const element = array[j];
        action.push(nbre[i].childNodes[j].lastChild.value);
        // console.log(le_dernier_cause(numero,cause_racine));
        console.log(nbre[i].childNodes[j].lastChild.value);
    }
    var cause = document.getElementById("dernier-pourquoi").textContent
    action.push(cause)
    // console.log("causecausecause",cause);
    action.push("pa"+numero);
    console.log("action========>",action);
    ACTION.push(action);
    action.push("|");
    console.log("ACTION========>",ACTION);
    }
      method = "POST";
      data = ACTION.toString();
      url = "http://127.0.0.1:9000/sonatel-sovar/analyse/saisi-pa";
      ajax(method, data, url);
      window.location.reload();
  });
});

// Fonction pour récuperer les derniérs pourquoi.............
function les_dernier_pourquoi(tmp){
  for (let i = 1; i < 7; i++) {
    if(document.getElementById(`input_5${i}`).value != ""){
      tmp.push(getElementById(`input_5${i}`).value)
    }else if(document.getElementById(`input_4${i}`).value != ""){
      tmp.push(document.getElementById(`input_4${i}`).value)
    }else if(document.getElementById(`input_3${i}`).value != ""){
      tmp.push(document.getElementById(`input_3${i}`).value)
    }else if(document.getElementById(`input_2${i}`).value != ""){
      tmp.push(document.getElementById(`input_2${i}`).value)
    }
  }
  console.log("dernier_pourquoi========>", tmp)
  return tmp;
}

// Stocker les derniéres pourquoi dans le sessionStorage lorsqu'on click sur le bouton.............
document.getElementById('action_programme').firstElementChild.addEventListener('click', (e)=>{
  //e.preventDefault()
  var causes_racines = []
  sessionStorage.setItem('causes_racines',les_dernier_pourquoi(causes_racines))

  //var pr = document.getElementById("pourquoi-5")
  //nbr_prq = pr.childElementCount
  //console.log("ezzzertt", nbr_prq);
  //console.log("ezzzertt", numero);
  //for (let index = 1; index < nbr_prq; index++) {
    //if (document.getElementById(`input_5${index}`).value != "") {
     // document.getElementById(`input_5${index}`).value
     // console.log("Value====>",document.getElementById(`input_5${index}`).value)
     // causes_racines.push(document.getElementById(`input_5${index}`).value)
    //}

  //}
  //sessionStorage.setItem('causes_racines',causes_racines)

})
