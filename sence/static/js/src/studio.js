function SenceStudioXBlock(runtime, element) {  
    $(element).find('.cancel-button').bind('click', function(e) {
      runtime.notify('cancel', {});
      e.preventDefault();
    });
  }
  