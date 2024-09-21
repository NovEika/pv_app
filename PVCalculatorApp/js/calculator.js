
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

            let hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'manual_input';
            hiddenInput.value = '1';
            formManual.appendChild(hiddenInput)

        }else if(dataTypeDatabase.checked){
            formManual.style.display = 'none';
            formDatabase.style.display = 'block';

            let hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'model_selection';
            hiddenInput.value = '1';
            formDatabase.appendChild(hiddenInput);

            let manualInput = document.querySelector('input[name="manual_input"]');
            if (manualInput) manualInput.remove();
    }
        })
    })

})