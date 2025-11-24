(function(){
    const flag = '{{ flag }}';
    const flag_decoded = atob(flag.split('').reverse().join(''));
    alert(flag_decoded);
})()