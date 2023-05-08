const bt = document.getElementById("definir_action")
bt.addEventListener('click',()=>{
    // console.log("Clicker");
    alert("Clicker")
})
// var liste_labelle = [
//     "Libelle Action",
//     "Porteurs",
//     "Echeance",
//   ];
//   var liste_id = [
//     "libelle_action",
//     "porteur_action",
//     "echeance_action",
//   ];
//   var data_acton = [];
  
//   function sous_bloc_action(parent, n, i, id, label) {
//     const div_ref = document.createElement("div");
//     div_ref.className = "col-3 d-flex flex-column";
//     label_ref = document.createElement("label");
//     label_ref.for = `${id}_${n}.${i}`;
//     label_ref.className = "d-flex justify-content-start";
//     label_ref.innerHTML = label;
//     input_ref = document.createElement("input");
//     input_ref.className = "fs-5 ps-2";
//     input_ref.id = `${id}_${n}.${i}`;
//     // console.log(input_ref.id);
//     input_ref.name = `${id}_${n}.${i}`;
//     //alert(label)
//     // if (label == "Code Action") {  // div permettant de referencier les actions parrapport pourquoi 5 
//     //   input_ref.value = `${id}_${n}.${i}`;
//     //   div_ref.style.display = "none"; // Cacher le div pour qu'il ne figure pas dams le formulaire d'actions
//     //   div_ref.className = "col-1";
//     // }
//     // if (label == "Ref Action") {
//     //   input_ref.value = `${id}_${n}.${i}`;
//     // }
//     if (label == "Libelle Action") {
//       div_ref.className = "col-5 d-flex flex-column";
//     }
//     if (label == "Porteur Acton") {
//       div_ref.className = "col-2 d-flex flex-column";
//     }
//     if (label == "Echeance Action") {
//       input_ref.type = "date";
//       div_ref.className = "col-2 d-flex flex-column";
//     }
  
//     div_ref.appendChild(label_ref);
//     div_ref.appendChild(input_ref);
//     parent.appendChild(div_ref);
  
//   }
  
//   function bloc_actions(parent, n) {
//     var i = form_input.childNodes.length;
//     const H3 = document.createElement("h3");
//     H3.innerHTML = `Action_n°${i}`;
//     H3.className = "modal-title fs-5 py-2";
//     const row = document.createElement("div");
//     row.className = "row mb-3";
//     row.id = `row_action_${n}`;
//     row.append(H3);
//     for (let index = 0; index < 5; index++) {
//       sous_bloc_action(row, n, i, liste_id[index], liste_labelle[index]);
//     }
//     parent.appendChild(row);
//   }
  
//   const form_actions = document.getElementById("form_actions");
//   const form_input = document.getElementById("form-input");
//   const recap_action = document.getElementById("recaputilatif");
//   const array = [];
  
//   document.querySelectorAll(".definir_action").forEach((element) => {
//     //element.addEventListener('click', ()=>{
//     $(element).on('click', function (e) {
//         alert('')
//         // console.log(element);
//         // e.preventDefault();
//         // var k = element.getAttribute('id').split('_').pop()
//         // var modal_title = document.getElementById(`input_5${k}_act`).value
//         // title = document.getElementById('modal_title')
//         // title.innerHTML = `Pourquoi 5${k} : `+ modal_title
//         // method = 'POST'
//         // data = 'reference_action_11'
//         // url = "http://127.0.0.1:5000/ajouter_action"
//         // console.log(url)
//         // // ajax(method, data, url)
//         $('#modal_action').modal('show');
//         // $(function () {
//         //   $('[data-toggle="tooltip"]').tooltip()
//         //   bloc_actions(form_input, k);
//         //   document.getElementById("autre-act").addEventListener('click', ()=>{
//         //     alert("form_input")
//         //     bloc_actions(form_input, element.getAttribute('id').split('_').pop());
//         //   })
//         // })
//     })
//   })
  
  
//   function ajax(method, data, Url) {
//     var url = new URL(window.location.href);
//     var id = document.getElementById("identifiant_act").value;
//     console.log(id);
//     var reference = document.getElementById("reference_av_act").value;
//     var id_va = url.searchParams.get("id_va");
//     var fichier_id = url.searchParams.get("fichier_id");
//     url = Url +'?fichier_id='+fichier_id+'&id_va='+id_va
//     console.log(url)
//     $.ajax({ 
//       data: { data: data }, //grab text between span tags
//       type: method,
//       url: url, //post grabbed text to flask endpoint for saving role
//       async: false,
//       success: function (data) {
//         console.log("Sent Successfully", url);
//       },
//       error: function (e) {
//         console.log("Submission failed...");
//       },
//     });
//   }
  
  
//   var ACTION = [];
//   var test = ["encore testons"];
//   $(document).ready(function () {
//     $("#bouton_valider_action").click(function (event) {
//       // event.preventDefault();
  
//       var nbre = document.getElementById("form-input").childNodes;
//       for (let i = 1; i < nbre.length; i++) {
//         var action = [];
//         for (let j = 1; j < nbre[i].childNodes.length; j++) {
//           //const element = array[j];
//           action.push(nbre[i].childNodes[j].lastChild.value);
//           console.log(nbre[i].childNodes[j].lastChild.value);
//         }
//         ACTION.push(action);
//         action.push("|");
//         console.log(ACTION);
//       }
//       method = "POST";
//       data = ACTION.toString();
//       url = "http://127.0.0.1:5000/ajouter_action";
//       ajax(method, data, url);
//       window.location.reload();
//     });
//   });
  
//   var element_statut_terminer = ['']
//   var element_courant
//   var exist
//   document.getElementById('enregistrement_de_detail').addEventListener('click', (e)=>{
//     // e.preventDefault()
//     alert('Voulez vous reellement terminer cette analyse ?')
//     element_statut_terminer = sessionStorage.getItem('element_statut_terminer')
//     if (element_statut_terminer){
//       element_statut_terminer = element_statut_terminer.split(',')
//       console.log(element_statut_terminer)
//       element_statut_terminer.forEach((element)=>{
//         if (element==element_courant){
//           exist = 1
//         }
//       })
//     }else {
//       element_statut_terminer = ['']
//     }
//     if (exist!=1){
//     element_courant = sessionStorage.getItem('element_courant')
//       element_statut_terminer.push(element_courant)
//     }
//     sessionStorage.setItem('element_statut_terminer', element_statut_terminer)
//   })
  
//   console.log(document.getElementById('libelle_av').value)
  
//   document.getElementById('action_programme').firstElementChild.addEventListener('click', (e)=>{
//     // e.preventDefault()
//     var causes_racines = []
//     causes_racines.push(document.getElementById('libelle_av').value)
//     var pr = document.getElementById("div-pourquoi5")
//     nbr_prq = pr.childElementCount
//     // console.log("ezzzertt", pr.childElementCount);
//     // for (let index = 1; index < nbr_prq +1; index++) {
//     //   if (document.getElementById(`input_5${index}_act`).value != "") {
//     //     document.getElementById(`input_5${index}_act`).value
//     //     causes_racines.push(document.getElementById(`input_5${index}_act`).value)
//     //   }
//     // }
//     // sessionStorage.setItem('causes_racines',causes_racines)
//   })
  