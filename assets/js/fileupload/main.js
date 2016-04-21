//this is the application.js file from the example code//
$(function () {
    'use strict';

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        acceptFileTypes: /(\.|\/)(jpe?g)$/i,
        previewMaxWidth: 400,
        previewMaxHeight: 900
    });
    
    // Enable iframe cross-domain access via redirect option:
    $('#fileupload').fileupload(
        'option',
        'redirect',
        window.location.href.replace(
            /\/[^\/]*$/,
            './cors/result.html?%s'
            )
        );
            
           $('#download-files > .template-download > .add').each(function(e){
                             

                                alert(e);

                                

                                });
            
           

            
       

    if (window.location.hostname === 'perrot-julien.fr') {
       
        // Upload server status check for browsers with CORS support:
        if ($.ajaxSettings.xhr().withCredentials !== undefined) {
            $.ajax({
                url: 'admin/get_files',
                dataType: 'json', 
                
                success : function(data) {  
                    var fu = $('#fileupload').data('fileupload'), 
                    template;
                    fu._adjustMaxNumberOfFiles(-data.length);
                    template = fu._renderDownload(data)
                    .appendTo($('#fileupload .files'));
                    
                    // Force reflow:
                    fu._reflow = fu._transition && template.length &&
                    template[0].offsetWidth;
                    template.addClass('in');
                    $('#loading').remove();
                }  
         
                
            }).fail(function () {
                $('<span class="alert alert-error"/>')
                .text('Upload server currently unavailable - ' +
                    new Date())
                .appendTo('#fileupload');
            });
        }
    } else {
        // Load existing files:
        $('#fileupload').each(function () {
            var that = this;
            $.getJSON(this.action, function (result) {
                if (result && result.length) {
                    $(that).fileupload('option', 'done')
                    .call(that, null, {
                        result: result
                    });
                }
            });
        });
    }


    // Open download dialogs via iframes,
    // to prevent aborting current uploads:
/*
    $('#fileupload .files a:not([target^=_blank])').live('click', function (e) {
        e.preventDefault();
        $('<iframe style="display:none;"></iframe>')
        .prop('src', this.href)
        .appendTo('body');
    });
*/
    $('#fileupload').bind('fileuploadsubmit', function (e, data) {
        var inputs = data.context.find(':input');
        if (inputs.filter('[required][value=""]').first().focus().length) {
            return false;
        }
        data.formData = inputs.serializeArray();
    });

    $('#fileupload').bind('fileuploadadd', function (e, data) {
        var previewHolders = $(".preview");
        previewHolders = previewHolders;
    })

    $('#fileupload').bind('fileuploadpreviewdone', function (e, data) {
        //var canvases = $(".preview .fade canvas");
        //canvases = canvases;
        
        var element = jQuery(e.originalEvent.target);
        var canvas = element.find('canvas');
        canvas.Jcrop({
            onSelect: updateCoords,
            aspectRatio: 1,
            coordsContainer: canvas.parent().next(),
            world: canvas
        });                
        
        //var bla = canvas;
        
    })

    function updateCoords(coords){
        var world = jQuery(this.getOptions().world);
        var wWidth = world.width();
        var wHeight = world.height();
        var strCoords = coords.x/wWidth + ',' + coords.y/wHeight + ',' + coords.x2/wWidth + ',' + coords.y2/wHeight;
        
        jQuery(this.getOptions().coordsContainer).val(strCoords);
    }

});