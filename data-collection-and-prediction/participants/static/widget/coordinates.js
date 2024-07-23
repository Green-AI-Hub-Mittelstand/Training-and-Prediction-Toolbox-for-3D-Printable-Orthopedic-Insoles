// Add your jQuery code to handle interactions with the image
$(document).ready(function () {



    function registerEventToMarking(markingDiv){
        markingDiv.on("click",function(e){
            e.stopPropagation();
            //$(this).remove();    
            //storeData();            
            showMarkingEditor($(this));
        });
    }

    function addMarking(left,top,pain){
        // Create a new div with the class 'marking'
        var markingDiv = $('<div>').addClass('marking');

        // Set the CSS properties
        markingDiv.css({
            'left': left + 'px',
            'top': top + 'px'                
        });

        markingDiv.attr("attr-x",left);
        markingDiv.attr("attr-y",top);
        markingDiv.attr("attr-pain",pain);
        markingDiv.html(pain);

        registerEventToMarking(markingDiv);

        // Append the div to the container
        $('#'+widgetId+'_image').append(markingDiv);

        return markingDiv;
    }


    function loadMarkings(){
        var value = $("#"+widgetId+"_input").val();
        console.log("value to load", value);
        console.log(value);

        // try to load the markings from json string
        var markingsFromJson = [];
        var dec = {};

        try{
            dec = JSON.parse(value);
            console.log(dec);
        }catch{
            console.error("could not parse json");
        }

        try{
            markingsFromJson = dec['markings'];
            if(markingsFromJson == undefined){
                throw new Error("no markings in field");
            }
            console.log(markingsFromJson);
        }catch{
            console.warn("could not find 'marking' field");
        }

        $.each(markingsFromJson, function(i,e){
            console.log(i,e);
            addMarking(e.x, e.y, e.pain);
        })
    }

    function storeData(){
        var markings = [];
        $("#"+widgetId+"_image .marking").each(function(i,e){
            //console.log(i,e);

            var x = $(e).attr('attr-x');
            var y = $(e).attr('attr-y');
            var pain = $(e).attr('attr-pain');

            markings.push({
                "x":x,
                "y":y,
                "pain":pain
            })
        });

        var data = {
            "markings":markings
        };

        $("#"+widgetId+"_input").val(JSON.stringify(data));
    }


    function hideMarkingEditor(){
        $('#marking-editor').hide();

    }

    function showMarkingEditor(marking){
        var x = parseFloat(marking.attr("attr-x"));
        var y = parseFloat(marking.attr("attr-y"));

        $('#marking-editor').show();

        $('#marking-editor').css({
            'left':(x+25) + "px",
            'top': y + "px"
        });

        $('#bt-save-marking-attr').off("click");
        $('#bt-delete-marking-attr').off("click");

        var currentPain = marking.attr('attr-pain');
        if(currentPain == null){
            currentPain = 3;
        }

        $('#painScale').val(currentPain);


        $('#bt-save-marking-attr').on("click",function(){
            marking.attr('attr-pain', $('#painScale').val());
            marking.html($('#painScale').val());
            hideMarkingEditor();
            storeData();
        });

        $('#bt-delete-marking-attr').on("click",function(){
            marking.remove();

            storeData();
            hideMarkingEditor();
        });
    }

    // Your jQuery code here
    $("#"+widgetId+"_image").on('click', function (event) { 

        var x = event.pageX - $(this).offset().left;
        var y = event.pageY - $(this).offset().top;

        

        // Calculate the position to center the marking div
        var left = x - 10;  // Half of the width (20px / 2)
        var top = y - 10;   // Half of the height (20px / 2)

        console.log(left, top);

        var marking = addMarking(left, top, 3);
        showMarkingEditor(marking);
        storeData();
    });

    $("#marking-editor").click(function(e){
        e.stopPropagation();
    })
    $('#marking-editor #close-button').click(function(){
        hideMarkingEditor();
        $('#painScale').val("1");
    });



    loadMarkings();
    hideMarkingEditor();
});