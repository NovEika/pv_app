function toggleDetails(itemId){
    let details = document.getElementById(`details-${itemId}`)

    if(details.style.display === "none"){
        details.style.display = "block";
    }else{
        details.style.display = "none";
    }
}