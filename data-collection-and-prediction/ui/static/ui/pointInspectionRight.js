function deepCopy(e) {
    return JSON.parse(JSON.stringify(e));
}

class POI_Right {
    constructor(data) {
        this.data = data;
        this.id = data.id;
        this.x = data.x;
        this.y = data.y;

    }
}

class State_Right {
    constructor(pois) {
        this.pois = pois;
        this.state = "this is a state object"
    }

    storeInDb(onRenderRequested) {
        console.log("storing in db");
        console.log(Urls.predictedpointrightList());
        // we need to find 
        //var foot = this.pois[0].data.foot;
        var foamPrintAnalysis = this.pois[0].data.predictions;
        var me = this;

        // get points in db
        $.ajax({
            
            url: Urls.predictedpointrightList() + "?predictions=" + foamPrintAnalysis,  // Replace <id> with the actual ID of the record you want to update
            method: 'GET',  // Use 'PUT' if needed

            contentType: 'application/json',
            success: function (response) {
                var pointsInDb = response;

                var pointsNotInDb = [];
                pointsInDb.forEach(pointInDb => {
                    // check if this point is still in the gui, if not, it needs to be deleted
                    var foundPoint = false;
                    me.pois.forEach((poi) => {
                        if (poi.id == pointInDb.id) {
                            foundPoint = true;
                        }
                    });
                    if (!foundPoint) {
                        console.log("DELETE POINT " + pointInDb.id);
                        $.ajax({
                            url: Urls.predictedpointright_detail(pointInDb.id),  // Replace <id> with the actual ID of the record you want to update
                            method: 'DELETE',  // Use 'PUT' if needed

                            contentType: 'application/json',
                            success: function (response) {
                                $.notify("Punkt " + pointInDb.id + " gelöscht", "success");
                                console.log('Record updated successfully:', response);
                            },
                            error: function (error) {
                                $.notify("Punkt " + poiData.id + " konnte nicht gelöscht werde", "warn");
                            }
                        });
                    }
                });

                me.pois.forEach((poi) => {
                    var poiData = poi.data;
                    console.log(poiData);


                    if (poi.id == -1) { // this point is not in the db yet, save it
                        $.ajax({
                            url: Urls.predictedpointright_detail(),  // Replace <id> with the actual ID of the record you want to update
                            method: 'POST',  // Use 'PUT' if needed
                            data: JSON.stringify(poiData),
                            contentType: 'application/json',
                            success: function (response) {
                                poi.data.id = response.id;
                                poi.id = poi.data.id;
                                if (typeof onRenderRequested === 'function') {
                                    onRenderRequested();
                                }
                                $.notify("Punkt " + response.id + " erstellt", "info");
                                console.log('Record updated successfully:', response);
                            },
                            error: function (error) {
                                $.notify("Punkt " + poiData.id + " konnte nicht erstellt werden", "warn");
                                console.log(error);
                            }
                        });
                    } else {
                        // check if this point is in the database, if not, delete it, if it is, update it



                        $.ajax({
                            url: Urls.predictedpointright_detail(poi.id),  // Replace <id> with the actual ID of the record you want to update
                            method: 'PATCH',  // Use 'PUT' if needed
                            data: JSON.stringify(poiData),
                            contentType: 'application/json',
                            success: function (response) {
                                $.notify("Punkt " + poiData.id + " gespeichert", "success");
                                console.log('Record updated successfully:', response);
                            },
                            error: function (error) {
                                $.notify("Punkt " + poiData.id + " konnte nicht gespeichert werde", "warn");
                                console.log(error);
                                if (error.status == 404) {

                                    // this point is already deleted, we create it newly
                                    $.ajax({
                                        url: Urls.predictedpointrightList(),  // Replace <id> with the actual ID of the record you want to update
                                        method: 'POST',  // Use 'PUT' if needed
                                        data: JSON.stringify(poiData),
                                        contentType: 'application/json',
                                        success: function (response) {
                                            poi.data.id = response.id;
                                            poi.id = poi.data.id;
                                            if (typeof onRenderRequested === 'function') {
                                                onRenderRequested();
                                            }
                                            $.notify("Punkt " + response.id + "neu erstellt", "warn");

                                        },
                                        error: function (error) {
                                            $.notify("Punkt " + poiData.id + " konnte nicht erstellt werden", "warn");
                                            console.log(error);
                                        }
                                    });
                                }
                            }
                        });



                    }

                    pointsNotInDb.forEach((pointNotInDb) => {
                        console.log("point to delete: " + pointNotInDb);
                    })


                });


            }
        })






    }


}

class StateHistory_Right {
    constructor() {
        this.states = [];
        this.currentState = null;
        this.historyIndex = -1;
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.currentState = this.states[this.historyIndex]
            $.notify("History Index: " + this.historyIndex, "info");
            return true;
        } else {
            return false;
        }
    }

    redo() {
        if (this.historyIndex < this.states.length - 1) {
            this.historyIndex++;
            $.notify("History Index: " + this.historyIndex, "info");
            this.currentState = this.states[this.historyIndex];
            return true;
        } else {
            return false;
        }
    }

    pushState(state) {
        var stateCopy = deepCopy(state)

        // delete all states that are after this history index
        this.states = this.states.slice(0, this.historyIndex + 1);

        var newState = new State_Right(stateCopy.pois);

        this.states.push(newState);
        this.historyIndex = this.states.length - 1;
        this.currentState = this.states[this.historyIndex];

        console.log(this);
    }


}


function renderPointEditorRight(container_id, image_url, points, foot, participant_id, allowEdit = true, initial_zoom = 0.5, window_width=700, window_height=1400, onMeassure = ()=>{}) {
    // Create HTML Stuff

    var canvas = null;
    var pointObjects = [];
    var labelObjects = [];

    var activePoint = null;
    var lastActivePoint = null;

    var zoom = initial_zoom;

    var brightness = 1;
    var contrast = 4;

    var colCanvas = $("<div class='col'></div>");
    var canvasElement = $("<canvas width='"+window_width+"' height='"+window_height+"' id='canvas-" + container_id + "' class='point-identifier' ></canvas>");
    colCanvas.append(canvasElement);
    $('#' + container_id).append(colCanvas);

    var contrastImg = null;

    if (allowEdit) {
        
        var colPanel = $("<div class='col'></div>");
        var panel = $('<div class="point-panel"></div>');
        colPanel.append(panel);

        var formTemplate = Handlebars.compile(poiForm);
        var formHTML = formTemplate({
            'id': container_id + "_id",
            'x': container_id + "_x",
            'y': container_id + "_y",
            'role': container_id + "_role",
            'choices': foamPointChoices,
            'img_url': image_url
        });

        panel.append(formHTML);
        $('#' + container_id).append(colPanel);

        var undoButton = colPanel.find(".undo");
        var redoButton = colPanel.find(".redo");
        var contrastButton = colPanel.find(".contrast");
        var saveButton = colPanel.find(".save");
        var deleteButton = colPanel.find(".delete");
        var newPointButton = colPanel.find(".new-point");
        var togglePointsButton = colPanel.find(".points");
        var contrastSlider = colPanel.find(".contrast-slider");
        contrastSlider.val(contrast);
    }


    // initialize history
    var stateHistory = new StateHistory_Right();

    // create the first state
    var currentState = new State_Right([]);
    points.forEach((point) => {
        currentState.pois.push(new POI_Right(point));
    });

    var foamPrintAnalysis = points[0].predictions;
    console.log("FoamPrintAnalysis", foamPrintAnalysis);

    stateHistory.pushState(currentState);

    function getStatus() {
        return new Promise((resolve) => {
            $.get(Urls.foamprintanalysis_detail(foamPrintAnalysis)).then((x) => {
                console.log("refreshing", foot);
                if (foot == "left") {

                    resolve(x.pointsLeftComplete)
                } else {
                    resolve(x.pointsRightComplete)
                }
            })
        })

    }

    function renderBool(b) {
        if (b) {
            return '<span style="color: green; font-size: 1.2em;">&#10003;</span>'
        } else {
            return '<span style="color: red; font-size: 1.2em;">&#10008;</span>'
        }


    }


    function renderStatus() {
        return new Promise((resolve) => {
            getStatus().then((status) => {
                console.log(status);

                var foundAllPoints = status.foundAllPoints;
                var missingPointsNum = status.missingPointsNum;
                var identifiedAllPoints = status.identifiedAllPoints;
                var unidentifiedPointsNum = status.unidentifiedPointsNum;
                var duplicatePointsNum = status.duplicatePointsNum;
                var ok = status.ok;
                var missingPointTypes = status.missingPointTypes.map((x) => {


                    return getLabelByChoiceIndex(x);
                });



                colPanel.find(".foundAllPoints").html(renderBool(foundAllPoints));
                colPanel.find(".missingPointsNum").html(missingPointsNum);
                colPanel.find(".identifiedAllPoints").html(renderBool(foundAllPoints));
                colPanel.find(".unidentifiedPointsNum").html(unidentifiedPointsNum);
                colPanel.find(".duplicatePointsNum").html(duplicatePointsNum);
                colPanel.find(".ok").html(renderBool(ok));
                colPanel.find(".missingPointTypes").html(missingPointTypes.map((x) => {
                    return "<li>" + x + "</li>"
                }));

                colPanel.find(".duplicatePoints").html(status.duplicatePoints.map((x) => {
                    return "<li>" + getLabelByChoiceIndex(x.pointType) + "</li>"
                }));

                resolve();
            })
        })

    }

    if(allowEdit){
        renderStatus();
    }

    

    //create deepcopy of initial state and replace it as the first state
    //without it first state gets overwritten by newest state (e.target)
    var initialState = new State_Right(deepCopy(stateHistory.states[0].pois))
    stateHistory.states[0] = initialState

    if (allowEdit) {
        saveButton.on("click", (e) => {
            console.log("currentState", stateHistory.currentState);
            stateHistory.currentState.storeInDb(() => {
                renderState(stateHistory.currentState);
            });
        })


        var refreshButton = colPanel.find(".refresh-status");

        refreshButton.click(() => {
            refreshButton.prop("disabled", true);
            renderStatus().then(() => {
                refreshButton.prop("disabled", false);
            })

        });

        contrastButton.on("click", () => {
            console.log("contrast");
            console.log(contrastImg);
            contrastImg.set({
                "visible": !contrastImg.get('visible')
            });
            canvas.renderAll();
        })

        contrastSlider.on("change", () => {
            contrast = contrastSlider.val();

            contrastImg.setSrc(Urls.renderEnhancedFootprint(participant_id, brightness, contrast, foot), () => {
                canvas.renderAll();
            })
        });

        togglePointsButton.on("click", () => {
            var pointsVisible = pointObjects[0].get("visible");
            var labelVisible = labelObjects[0].get("visible");



            // if both are visible            
            if (pointsVisible && labelVisible){
                // hide just the labels
                pointObjects.forEach((p) => {
    
                    p.textbox.set({
                        "visible": false
                    })
                });
    
            }

            // if just the points are visible
            if(pointsVisible && !labelVisible){
                // hide just the points
                pointObjects.forEach((p) => {

                    p.set({
                        "visible": false
                    })
                });
            } 

            // if none is visible
            if(!pointsVisible && !labelVisible){
                // hide just the points
                pointObjects.forEach((p) => {

                    p.set({
                        "visible": true
                    })

                    p.textbox.set({
                        "visible": true
                    })
                });
            } 

           


            canvas.renderAll();
        })

    }







    // Initialize Fabric.js canvas
    canvas = new fabric.Canvas("canvas-" + container_id);
    canvas.setZoom(zoom);

    var selectedPoint = null;

    if(allowEdit){
        deleteButton.on("click", function () {
            if (selectedPoint) {
                canvas.remove(selectedPoint);
    
                // and remove it from the point list
                var numBefore = pointObjects.length;
    
                pointObjects = pointObjects.filter(function (x) {
                    return x !== selectedPoint;
                });
    
                var numAfter = pointObjects.length;
    
                if (numBefore == numAfter) {
                    $.notify("Punkt konnte nicht gelöscht werden", "warn");
                }
    
                var s = getState();
                stateHistory.pushState(s);
            } else {
                $.notify("Kein Punkt ausgewählt", "warn");
            }
        })
    
        newPointButton.on("click", function () {
            if (pointObjects.length > 0) {
                var data = {
                    "foamPrintAnalysis": pointObjects[0].greenAiInstance.predictions,
                    "foot": pointObjects[0].greenAiInstance.foot,
                    "x": 700,
                    "y": 700,
                    "pointType": -1,
                    "id": -1
                }
    
                renderPoint(data);
                var s = getState();
                stateHistory.pushState(s);
    
            } else {
                $.notify("Keine Punkte gefunden", "warn")
            }
        })
    }

    


    function getLabelByChoiceIndex(index) {
        var index = parseInt(index);
        var label = "xxx";
        foamPointChoicesShort.forEach((choice) => {

            if (choice[0] == index) {
                label = choice[1];
            }
        });

        return label;
    }


    var activeColor = '#f736c4';
    var secondaryActiveColor = '#b8fbff';
    var defaultColor = '#54d911';
    var defaultOpacity = 0.5;


    function colorPoints(){
        if(lastActivePoint != null){
            lastActivePoint.set({
                'fill':secondaryActiveColor,
                'opacity':1
            })

        }

        if(activePoint!=null){
            activePoint.set({
                'fill':activeColor,
                'opacity':1
            })

        }

    }


    var distanceTextbox = new fabric.Textbox("", {
        left: 50,
        top: 50,
        hasBorders: false,
        hasControls: false,
        selectable: false,
        transparentCorners: true,
        fontFamily: "Helvetica",
        width: 350,
        height: 50,
        textBackgroundColor: "#fff",
        zIndex:100,
        fill: '#000'
    });

    canvas.add(distanceTextbox);



    function renderPoint(element) {
        var radius = 20;


        


        item = new fabric.Circle({
            radius: radius,
            fill: defaultColor,
            opacity: defaultOpacity,
            selectable:allowEdit,
            hasBorders: false,
            hasControls: false,
            originX: 'center',
            originY: 'center',
            top: element.y,
            left: element.x,
            greenAiInstance: element,
            zIndex: 3
        })


        if (activePoint != null){
            if (activePoint.greenAiInstance.id == element.id){
                activePoint = item;
            }
        }



        if (lastActivePoint != null){
            if (lastActivePoint.greenAiInstance.id == element.id){
                lastActivePoint = item;
            }
        }

        //create new textbox below each point stating role
        //issues with undo

        // try and get the short label


        var label = getLabelByChoiceIndex(item.greenAiInstance.pointType);

        //foamPointChoicesShort[parseInt(item.greenAiInstance.pointType,10)+1][1];

        function calculateDistance(point1, point2) {
            var dx = point2.left - point1.left;
            var dy = point2.top - point1.top;
            var distance = Math.sqrt(dx * dx + dy * dy);
            return distance;
        }

        

        function meassure(){
            if(activePoint!= null && lastActivePoint != null){
                var dist = calculateDistance(activePoint, lastActivePoint)
                console.log(dist);
                distanceTextbox.bringToFront();
                distanceTextbox.set('text'," " + Math.floor(dist/10) + "mm");
                onMeassure(Math.floor(dist/10));
                canvas.renderAll();
                
            }
            


            //console.log(activePoint, lastActivePoint);
        }

        var textbox = new fabric.Textbox(label, {
            left: item.left,
            top: item.top + radius * 2,
            hasBorders: false,
            hasControls: false,
            selectable: false,
            transparentCorners: true,
            fontFamily: "Helvetica",
            // width: 350,
            height: 50,
            textBackgroundColor: "#fff",

            fill: '#000'
        });

        //assign textbox to the point
        item.textbox = textbox

        canvas.add(item);
        canvas.add(textbox);
        pointObjects.push(item);
        labelObjects.push(textbox)

        setEvents = function (i) {
            i.on("mousedown", function (e) {

                $('#' + container_id + "_id").val(e.target.greenAiInstance.id);
                $('#' + container_id + "_x").val(e.target.left);
                $('#' + container_id + "_y").val(e.target.top);
                $('#' + container_id + "_role").val(e.target.greenAiInstance.pointType);



                selectedPoint = e.target;

                if (lastActivePoint != null){
                    lastActivePoint.set({
                        'fill':defaultColor,
                        'opacity':defaultOpacity
                    })
                }


                lastActivePoint = activePoint;
                activePoint = e.target;

                colorPoints();                
                canvas.renderAll();

                meassure();


            });

            i.on('moving', function () {
                textbox.set({ left: i.left, top: i.top + radius * 2 });
                textbox.setCoords();  //update coordinates of the textbox's bounding box
                canvas.renderAll();

                meassure();

            });

            $('#' + container_id + "_role").off("change").on("change", (evnt) => {
                if (selectedPoint) {
                    var val = $('#' + container_id + "_role").val();
                    selectedPoint.greenAiInstance.pointType = val;
                    selectedPoint.textbox.text = foamPointChoices[parseInt(val, 10) + 1][1];
                    canvas.renderAll();
                    // issue is initial state is not in statehistory
                    stateHistory.pushState(getState())

                }

            });


        }
        setEvents(item);

    }



    function getState() {



        // create new points
        var newPoints = [];


        pointObjects.forEach((e) => {
            var data = deepCopy(e.greenAiInstance);

            var p = new POI_Right(data);
            p.data.x = Math.round(e.left);
            p.data.y = Math.round(e.top);

            newPoints.push(p);


        })
        return new State_Right(newPoints);
    }

    function renderState(state) {
        selectedPoint = null;
        pointObjects.forEach((e) => {
            canvas.remove(e);
            canvas.remove(e.textbox)
        });

        pointObjects = [];
        labelObjects = [];

        state.pois.forEach(element => {
            //deepcopy here needed to not overwrite previous state after undo+role change
            element = deepCopy(element.data);


            renderPoint(element);


        });

        colorPoints();
        canvas.renderAll();

    }

    if (allowEdit){
        undoButton.on("click", (e) => {
            stateHistory.undo();
            renderState(stateHistory.currentState);
        })
    
    
        redoButton.on("click", (e) => {
            stateHistory.redo();
            renderState(stateHistory.currentState);
        })
    
    
    
        canvas.on("object:modified", (e) => {
            var s = getState();
            stateHistory.pushState(s);
    
    
        });
    
    }
    

    // Load an image onto the canvas
    fabric.Image.fromURL(Urls.renderEnhancedFootprint(participant_id, brightness, contrast, foot), function (img) {
        // Set the image properties
        img.set({
            left: 0,
            top: 0,
            zIndex: 2,
            hoverCursor: "default",
            selectable: false, // Allow the image to be selected
        });

        // Add the image to the canvas
        canvas.add(img);

        // Set coordinates (left and top) for the image
        img.set({
            left: 0,
            top: 0,
            zIndex: 2
        });

        contrastImg = img;

        renderState(stateHistory.currentState);

        // Render the canvas
        canvas.renderAll();

    });


    // Load an image onto the canvas
    fabric.Image.fromURL(image_url, function (img) {
        // Set the image properties
        img.set({
            left: 0,
            top: 0,
            zIndex: 1,
            hoverCursor: "default",
            selectable: false, // Allow the image to be selected
        });

        // Add the image to the canvas
        canvas.add(img);

        // Set coordinates (left and top) for the image
        img.set({
            left: 0,
            top: 0,
            zIndex: 1
        });

        renderState(stateHistory.currentState);

        // Render the canvas
        canvas.renderAll();


    });



    // Enable zooming functionality
    canvas.on('mouse:wheel', function (options) {
        if (options.e.ctrlKey) {
            var delta = options.e.deltaY;
            
            zoom = zoom + delta / 2000;
            console.log(zoom, delta);

            // Set limits for zooming
            if (zoom > 2) zoom = 2;
            if (zoom < 0.1) zoom = 0.1;

            // Set the new zoom level
            canvas.setZoom(zoom);
            options.e.preventDefault();
            options.e.stopPropagation();
        }
    });

    canvas.setZoom(initial_zoom);

    /// panning
    // Set initial pan variables
    var isPanning = false;
    var panStartX = 0;
    var panStartY = 0;

    // Handle mouse down event to start panning (only for the middle mouse button)
    canvas.on('mouse:down', function (event) {
        if (event.e.ctrlKey) { // Check if the middle mouse button is pressed
            isPanning = true;
            panStartX = event.e.clientX;
            panStartY = event.e.clientY;
        }
    });

    // Handle mouse move event to pan the canvas
    canvas.on('mouse:move', function (event) {
        if (isPanning) {
            var deltaX = event.e.clientX - panStartX;
            var deltaY = event.e.clientY - panStartY;

            canvas.relativePan({ x: deltaX, y: deltaY });
            panStartX = event.e.clientX;
            panStartY = event.e.clientY;


        }
    });

    // Handle mouse up event to stop panning
    canvas.on('mouse:up', function () {
        isPanning = false;
    });

    return points;



}