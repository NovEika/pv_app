
document.addEventListener('DOMContentLoaded', function(event){
    const radioButtons = document.getElementsByName('data_type');
    const dataTypeManual = document.getElementById('manual');
    const dataTypeDatabase = document.getElementById('database');
    const formManual = document.getElementById('manual_form');
    const formDatabase = document.getElementById('database_form');

    radioButtons.forEach(radio => {
        radio.addEventListener('change', function(){
         if(dataTypeManual.checked){
            formManual.style.display = 'block';
            formDatabase.style.display = 'none';
        }else if(dataTypeDatabase.checked){
            formManual.style.display = 'none';
            formDatabase.style.display = 'block';
    }
        })
    })

})