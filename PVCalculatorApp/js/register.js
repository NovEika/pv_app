
document.addEventListener('DOMContentLoaded', function() {
    let roleField = document.getElementById('id_role')
    let groupLeaderField = document.getElementById('id_group_leader')

    function toggleGroupLeaderField(){
        if(roleField.value === 'engineer'){
            groupLeaderField.style.display = 'block';
        }
        else{
            groupLeaderField.style.display = 'none';
        }
    }
    toggleGroupLeaderField();
    roleField.addEventListener('change', toggleGroupLeaderField);
});