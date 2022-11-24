function AnnoEstudiante(){
    tipoPersona = document.getElementById("tipoBuscarPersona");
    if(tipoPersona.disabled== false){
        if(tipoPersona.selectedIndex == 2){
            console.log("Entro");
            document.getElementById("Check1").disabled = false;
            document.getElementById("Check2").disabled = false;
            document.getElementById("Check3").disabled = false;
            document.getElementById("Check4").disabled = false;
        }else if(document.getElementById("Check1").disabled == false){
            document.getElementById("Check1").disabled = true;
            document.getElementById("Check2").disabled = true;
            document.getElementById("Check3").disabled = true;
            document.getElementById("Check4").disabled = true;
        }

    }
}

function SeleccionarTodo(){
    console.log("entro al seleccionar todo")
    console.log(document.getElementById("seleccionar_todo"))
    if(document.getElementById("seleccionar_todo")){
        console.log("ya esta en el if de seleccionar todo")
        var checkboxlist = document.getElementsByClassName("Checklist")
        console.log(checkboxlist.length)
        for (var i = 0; i < checkboxlist.length; i++){
            console.log("for")
            console.log(checkboxlist[i])
            checkboxlist[i].checked = true
        }
    }
}
