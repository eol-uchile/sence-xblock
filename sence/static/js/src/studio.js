function SenceStudioXBlock(runtime, element) {  

  var handlerUrl = runtime.handlerUrl(element, 'save_students_codes');
  
    $(element).find('.save-students-codes-button').bind('click', function(e) {
      var form_data = new FormData();
      var students_codes = $(element).find('textarea[name=students_codes]').val();
      form_data.append('students_codes', students_codes);
      runtime.notify('save', {state: 'start'});
      $.ajax({
        url: handlerUrl,
        dataType: 'text',
        cache: false,
        contentType: false,
        processData: false,
        data: form_data,
        type: "POST",
        success: function(data){
          runtime.notify('save', {state: 'end'});
        },
        error: function(data){
          response = JSON.parse(data.responseText)
          if(response.result == 'error'){
            $(element).find('.error-message').html(response.message);
          }
        }
      });
      e.preventDefault();
  
    });


    $(element).find('.cancel-button').bind('click', function(e) {
      runtime.notify('cancel', {});
      e.preventDefault();
    });
  }
  