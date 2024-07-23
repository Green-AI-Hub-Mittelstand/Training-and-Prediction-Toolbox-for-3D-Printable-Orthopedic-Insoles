function deepCopy(e) {
    return JSON.parse(JSON.stringify(e));
}


class PressureMatchingEditor {

    constructor(container_id, foam_url, foam_url_enhanced, points, pressure_url, foot, training_id, pressure_alignment, csv_filename, fit_quality, participant_id, initial_zoom = 0.5, window_width=700, window_height=1400) {
        this.container_id = container_id;
        this.foam_url = foam_url;
        this.foam_url_enhanced = foam_url_enhanced;
        this.points = points;
        this.pressure_url = pressure_url;
        this.foot = foot;
        this.training_id = training_id;
        this.pressure_alignment = pressure_alignment;
        this.csv_filename = csv_filename;
        this.fit_quality = fit_quality;
        this.participant_id = participant_id;

        this.initial_zoom = initial_zoom;
        this.window_width = window_width;
        this.window_height = window_height;

        

        this.prevY = -1;
        this.prevX = -1;
        this.prevRot = -1;

        this.contrast = 1;
        this.brightness = 2;

        this.highContrastViewVisible = false;

        this.createHtmlElements();

        this.populateData();

        this.createCanvas();

        this.setButtonEvents();


    }

    onClean() {
        this.copyButton.prop("disabled", false);
        this.saveButton.prop("disabled", true);
        $('#' + this.container_id + "_y").removeClass("edited");
        $('#' + this.container_id + "_rot").removeClass("edited");
        $('#' + this.container_id + "_x").removeClass("edited");
        $('#' + this.container_id + "_quality").removeClass("edited");
    }

    onDirty() {
        this.saveButton.prop("disabled", false);
        this.copyButton.prop("disabled", true);
        console.log("dirty");
        $('#' + this.container_id + "_y").addClass("edited");
        $('#' + this.container_id + "_rot").addClass("edited");
        $('#' + this.container_id + "_x").addClass("edited");   
        $('#' + this.container_id + "_quality").addClass("edited"); 
    }

    setPressureAlignment(_alignment) {
        console.log("alignment to copy:",_alignment);
        this.pressure_alignment = _alignment;
        var _this = this;
        this.pressureImg.set({
            angle: _this.pressure_alignment.rot,
            left: Math.floor(_this.pressure_alignment.x),
            top: Math.floor(_this.pressure_alignment.y),
        })

        this.onDirty();

        $('#' + this.container_id + "_rot").val(this.pressure_alignment.rot)
        $('#' + this.container_id + "_x").val(_this.pressure_alignment.x)
        $('#' + this.container_id + "_y").val(_this.pressure_alignment.y)

        this.saveButton.prop("disabled", false);

        this.canvas.renderAll();

    }

    createHtmlElements() {
        var colCanvas = $("<div class='col'></div>");
        this.canvasElement = $("<canvas width='"+this.window_width+"' height='"+this.window_height+"' id='canvas-" + this.container_id + "' class='point-identifier' ></canvas>");
        colCanvas.append(this.canvasElement);
        $('#' + this.container_id).append(colCanvas);
        this.colPanel = $("<div class='col'></div>");
        this.panel = $('<div class="point-panel"></div>');
        this.colPanel.append(this.panel);
        this.populatePanel();
    }

    populatePanel() {
        var formTemplate = Handlebars.compile(matchingForm);

        var templateContext = {
            'id': this.container_id + "_id",
            'x': this.container_id + "_x",
            'y': this.container_id + "_y",
            'rot': this.container_id + "_rot",
            'quality': this.container_id + "_quality",
            'pressure_url': this.pressure_url,
            'csv_filename': this.csv_filename,
            'foot': this.foot
        };

        var formHTML = formTemplate(templateContext);


        this.panel.append(formHTML);
        $('#' + this.container_id).append(this.colPanel);
    }

    populateData() {
        $('#' + this.container_id + "_id").val(this.training_id);
        $('#' + this.container_id + "_quality").val(this.fit_quality);
        
    }

    copyToOthers() {
        var _this = this;
        editors.forEach((editor) => {
            if (editor.foot == _this.foot && editor.container_id != _this.container_id) {
                if (editor.pressure_alignment.rot == 0) {
                    editor.setPressureAlignment(_this.pressure_alignment);
                }
            }
        });
    }

    setButtonEvents() {
        var _this = this;
        $('#' + this.container_id + "_quality").on("change", ()=>{
            _this.onDirty();
        })

        this.saveButton = this.colPanel.find(".save");
        this.resetButton = this.colPanel.find(".reset");
        this.toggleViewButton = this.colPanel.find(".toggleView");
        this.copyButton = this.colPanel.find(".copy");
        this.togglePressureViewButton = this.colPanel.find(".togglePressureView");

        this.currentContrastLabel  = this.colPanel.find(".current-contrast");
        this.currentBrightnessLabel  = this.colPanel.find(".current-brightness");

        this.contrastSlider = this.colPanel.find(".contrast-slider");
        this.brightnessSlider = this.colPanel.find(".brightness-slider");

        console.log("contrastSlider",this.contrastSlider);
        console.log("brightnessSlider",this.brightnessSlider);

        var _this = this;


        this.contrastSlider.val(this.contrast);
        this.brightnessSlider.val(this.brightness);
        
        _this.currentContrastLabel.text(_this.contrastSlider.val());
        _this.currentBrightnessLabel.text(_this.brightnessSlider.val());


        
        function updateFoamRender(){
            console.log("updateFoamRender", );
            _this.contrast = _this.contrastSlider.val();
            _this.brightness = _this.brightnessSlider.val();

           

            console.log("updateFoamRender","contrast", _this.contrast,"brightness", _this.brightness);

            _this.highContrastViewVisible = true;
            
            _this.enhanced_image.set({
                visible: _this.highContrastViewVisible
            })

            var newUrl = Urls.renderEnhancedFootprint(_this.participant_id, _this.contrast, _this.brightness, _this.foot);
            console.log(newUrl);

            _this.enhanced_image.setSrc(newUrl, ()=>{
                _this.canvas.renderAll();
            })
        }

        this.contrastSlider.on("change",updateFoamRender);
        this.brightnessSlider.on("change",updateFoamRender);

        function updateRenderLabels(){
            _this.currentContrastLabel.text(_this.contrastSlider.val());
            _this.currentBrightnessLabel.text(_this.brightnessSlider.val());
        }

        this.contrastSlider.on("input", updateRenderLabels);
        this.brightnessSlider.on("input", updateRenderLabels);

        


        this.toggleViewButton.on("click", () => {
            _this.highContrastViewVisible = !_this.highContrastViewVisible;
            _this.enhanced_image.set({
                visible: _this.highContrastViewVisible
            })
            this.canvas.renderAll();
        })

        this.togglePressureViewButton.on("click", () => {
            
            _this.pressureImg.set({
                visible: !_this.pressureImg.get("visible")
            })
            this.canvas.renderAll();
        })

        this.saveButton.prop("disabled", true);


        this.resetButton.on("click", $.proxy(this.reset, this));

        this.copyButton.on("click", $.proxy(this.copyToOthers, this));


        this.saveButton.on("click", (e) => {
            var updatedData = {
                pressure_x: Math.ceil(this.pressureImg.get("left")),
                pressure_y: Math.ceil(this.pressureImg.get("top")),
                pressure_rot: this.pressureImg.get("angle"),
                fit_quality: $('#' + this.container_id + "_quality").val()
            }

            $.ajax({
                url: Urls.trainingdataDetail(this.training_id),
                method: "PATCH",
                contentType: "application/json",
                data: JSON.stringify(updatedData),
                success: () => {
                    $.notify("Translation und Rotation gespeichert", "success");

                    this.prevX = updatedData['pressure_x'];
                    this.prevY = updatedData['pressure_y'];
                    this.prevRot = updatedData['pressure_rot'];

                    this.onClean();

                },
                error: function (error) {
                    $.notify("Translation und Rotation gespeichert konnte nicht gespeichert werde", "warn");
                }
            });

            
        });


    }

    createCanvas() {
        this.pressureImg = null;
        // Initialize Fabric.js canvas
        this.canvas = new fabric.Canvas("canvas-" + this.container_id);
        

        this.enhanced_image = false;

        var _this = this;


        fabric.Image.fromURL(this.foam_url, function (foam_img) {


            foam_img.set({
                left: 0,
                top: 0,
                zIndex: 0,
                hoverCursor: "default",
                selectable: false, // Allow the image to be selected
            });

            // Add the image to the canvas
            _this.canvas.add(foam_img);

            // Set coordinates (left and top) for the image
            foam_img.set({
                left: 0,
                top: 0,
                zIndex: 0
            });


            // Load an image onto the canvas
            fabric.Image.fromURL(Urls.renderEnhancedFootprint(_this.participant_id, _this.brightness, _this.contrast, _this.foot), function (foam_img_enhanced) {
                // Set the image properties
                _this.enhanced_image = foam_img_enhanced;

                foam_img_enhanced.set({
                    left: 0,
                    top: 0,
                    zIndex: 1,
                    visible: false,
                    hoverCursor: "default",
                    selectable: false, // Allow the image to be selected
                });

                // Add the image to the canvas
                _this.canvas.add(foam_img_enhanced);

                // Set coordinates (left and top) for the image
                foam_img_enhanced.set({
                    left: 0,
                    top: 0,
                    zIndex: 1
                });

                //renderState(stateHistory.currentState);

                // Render the canvas
                _this.canvas.renderAll();

                fabric.Image.fromURL(_this.pressure_url, function (pressure_img) {
                    _this.pressureImg = pressure_img;
                    pressure_img.set({
                        zIndex: 10,

                        originX: "center",
                        originY: "center",
                        angle: _this.pressure_alignment.rot,
                        left: Math.floor(_this.pressure_alignment.x),
                        top: Math.floor(_this.pressure_alignment.y),
                        lockScalingX: true,
                        lockScalingX: true,
                        hoverCursor: "default",
                        selectable: true, // Allow the image to be selected


                    });


                    _this.canvas.add(pressure_img);

                    var width = pressure_img.get("width");
                    var height = pressure_img.get("height");


                    var x = pressure_img.get("left");
                    var y = pressure_img.get("top");

                    if (x == 0 && y == 0) {

                        
                        var mod = {
                            left: width / 2,
                            top: height / 2
                        };
                        
                        pressure_img.set(mod);
                    }


                    _this.canvas.renderAll();

                    $('#' + _this.container_id + "_id").val(_this.training_id)
                    $('#' + _this.container_id + "_rot").val(_this.pressureImg.angle)
                    $('#' + _this.container_id + "_x").val(_this.pressureImg.left)
                    $('#' + _this.container_id + "_y").val(_this.pressureImg.top)

                    _this.prevY = _this.pressureImg.top;
                    _this.prevX = _this.pressureImg.left;
                    _this.prevRot = _this.pressureImg.angle;

                });


            });
        });

        this.setCanvasEvents();

    }

    setCanvasEvents() {
        var _this = this;
        this.canvas.on("object:modified", (e) => {

            $('#' + _this.container_id + "_id").val(_this.training_id)

            if (_this.pressureImg) {

                _this.pressure_alignment.x = _this.pressureImg.left;
                _this.pressure_alignment.y = _this.pressureImg.top;
                _this.pressure_alignment.rot = _this.pressureImg.angle;

                $('#' + _this.container_id + "_rot").val(_this.pressureImg.angle)
                $('#' + _this.container_id + "_x").val(_this.pressureImg.left)
                $('#' + _this.container_id + "_y").val(_this.pressureImg.top)

                _this.onDirty();
            }

        });



        // Enable zooming functionality
        this.canvas.on('mouse:wheel', function (options) {
            console.log("mouse wheel");
            if (options.e.ctrlKey) {
                var delta = options.e.deltaY;
                var zoom = _this.canvas.getZoom();
                zoom = zoom + delta / 2000;
                console.log(zoom, delta);

                // Set limits for zooming
                if (zoom > 2) zoom = 2;
                if (zoom < 0.1) zoom = 0.1;

                // Set the new zoom level
                _this.canvas.setZoom(zoom);
                options.e.preventDefault();
                options.e.stopPropagation();
            }
        });

        this.canvas.setZoom(this.initial_zoom);

        /// panning
        // Set initial pan variables
        var isPanning = false;
        var panStartX = 0;
        var panStartY = 0;

        // Handle mouse down event to start panning (only for the middle mouse button)
        this.canvas.on('mouse:down', function (event) {
            if (event.e.ctrlKey) { // Check if the middle mouse button is pressed
                isPanning = true;
                panStartX = event.e.clientX;
                panStartY = event.e.clientY;
            }
        });

        // Handle mouse move event to pan the canvas
        this.canvas.on('mouse:move', function (event) {
            if (isPanning) {
                var deltaX = event.e.clientX - panStartX;
                var deltaY = event.e.clientY - panStartY;

                _this.canvas.relativePan({ x: deltaX, y: deltaY });
                panStartX = event.e.clientX;
                panStartY = event.e.clientY;


            }
        });

        // Handle mouse up event to stop panning
        this.canvas.on('mouse:up', function () {
            isPanning = false;
        });


        _this.canvas.relativePan({ x: 50, y: 50 });
    }

    reset() {
        this.pressureImg.set("left", this.prevX);
        this.pressureImg.set("top", this.prevY);
        this.pressureImg.set("angle", this.prevRot);

        this.pressure_alignment.x = this.prevX;
        this.pressure_alignment.y = this.prevY;
        this.pressure_alignment.rot = this.prevRot;

        $('#' + this.container_id + "_y").removeClass("edited");
        $('#' + this.container_id + "_rot").removeClass("edited");
        $('#' + this.container_id + "_x").removeClass("edited");
        $('#' + this.container_id + "_rot").val(this.prevRot)
        $('#' + this.container_id + "_x").val(this.prevX)
        $('#' + this.container_id + "_y").val(this.prevY)
        this.saveButton.prop("disabled", true);
        this.canvas.renderAll();
    }



}



function matchingEditor(container_id, foam_url, foam_url_enhanced, points, pressure_url, foot, training_id, pressure_alignment, csv_filename, fit_quality, participant_id, initial_zoom = 0.5, window_width=700, window_height=1400) {
    var me = new PressureMatchingEditor(container_id, foam_url, foam_url_enhanced, points, pressure_url, foot, training_id, pressure_alignment, csv_filename, fit_quality, participant_id, initial_zoom, window_width, window_height);

    return me;


}