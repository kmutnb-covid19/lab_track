$(function() {
    $("form[name='login']").validate({
    rules: {
        username: {
            required: true,
        },
        password: {
            required: true,
            
        }
    },
    messages: {
        username: "Please enter a valid username",
        password: {
          required: "Please enter password",
        }    
    },
    submitHandler: function(form) {
        form.submit();
    }
    });
});