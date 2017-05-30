/**
 * Created by mefesto on 24.05.17.
 */
$(document).ready(function () {
   $('#files-upload').click(function () {
      $('#first-textarea').hide();
      $('#second-textarea').hide();
      $('#first-input-button').show();
      $('#second-input-button').show();
   });
   $('#textareas-upload').click(function () {
      $('#first-textarea').show();
      $('#second-textarea').show();
      $('#first-input-button').hide();
      $('#second-input-button').hide();
   });

   $('#copy-to-clipboard').click(function () {
       new Clipboard('#copy-to-clipboard');
   });

   $('#copy-to-clipboard-2').click(function () {
       new Clipboard('#copy-to-clipboard-2');
   });

   $('#view-crt-file').click(function () {
       $.ajax({
           type: 'GET',
           dataType: 'json',
           data: {'pk': document.URL.split('/')[4]},
           success: function (data) {
               $('#crt').val(data['crt']);
               $('#key').val(data['key']);
           }
       })
   });

    $('#id_validity_period').attr('type', 'text').mask('9999-99-99')

});