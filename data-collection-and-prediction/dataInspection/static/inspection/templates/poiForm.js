var poiForm = `

<div class="container">
    <div class="row">
        <div class="col-4">


            <div class="btn-toolbar" role="toolbar" style="margin-bottom:3px">

                <!-- Undo Button -->
                <button type="button" class="btn btn-light me-2 undo" title="Undo">
                    <i class="fas fa-undo"></i>
                </button>
            
                <!-- Redo Button -->
                <button type="button" class="btn btn-light me-2 redo" title="Redo">
                    <i class="fas fa-redo"></i>
                </button>
            
                <!-- Save Button -->
                <button type="button" class="btn btn-light me-2 save" title="Save">
                    <i class="fas fa-save"></i>
                </button>
            
              </div>
            
              <div class="btn-toolbar" role="toolbar"  style="margin-bottom:3px"> 
                <!-- Undo Button -->
                <button type="button" class="btn btn-light me-2 new-point " title="Neuer Punkt">
                    <i class="fas fa-add"></i>
                </button>
            
                <!-- Redo Button -->
                <button type="button" class="btn btn-light me-2 delete" title="Löschen">
                    <i class="fas fa-trash"></i>
                </button>
            
                <!-- Save Button -->
                
              </div>
            
            
            
            
              
              <div class="btn-toolbar" role="toolbar"  style="margin-bottom:3px">
                
                
                <button type="button" class="btn btn-light me-2 contrast" title="Kontrast umschalten">
                    <i class="fa-solid fa-circle-half-stroke"></i>
                </button>
            
                
                <button type="button" class="btn btn-light me-2 points " title="Punkte umstellen">
                    <i class="fa-solid fa-eye-slash"></i>
                </button>
            
                
              </div>
            
            
            
            <input type="range" min="1" max="10" value="50" class="contrast-slider" >
            
            


        </div>
        <div class="col">
            <div class="row">
                <div class="container">
                    <div class="row">
                        <div class="col">
                            <strong>Status</strong>
                        </div>
                        <div class="col">
                            <button type="button" class="btn btn-small btn-light refresh-status " title="Status aktualisieren">
                                <i class="fa-solid fa-rotate-right"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                

                
                <hr> <br>
                <table>
                    <tr>
                        <th>
                            Alles Ok
                        </th>
                        <td>
                            <span class="ok"></span>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Alle Markierungen gefunden
                        </th>
                        <td>
                            <span class="foundAllPoints"></span>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Anzahl nicht gefundener Markierungen
                        </th>
                        <td>
                            <span class="missingPointsNum"></span>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Alle Punkte identifiziert
                        </th>
                        <td>
                            <span class="identifiedAllPoints"></span>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Anzahl nicht identifizierter Punkte
                        </th>
                        <td>
                            <span class="unidentifiedPointsNum"></span>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Fehlende Punkttypen
                        </th>
                        <td>
                            <ul class="missingPointTypes"></li>
                        </td>
                    </tr>

                    <tr>
                        <th>
                            Anzahl doppelter Punkte
                        </th>
                        <td>
                            <span class="duplicatePointsNum"></span>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Doppelte Punkte
                        </th>
                        <td>
                            <ul class="duplicatePoints">

                            </ul>
                        </td>
                    </tr>
                    

                    
                    
                    
                    
                </table>



                

















            </div>
        </div>
    </div> 
</div>



<br><hr><br>


<form>
    {{!-- ID Field --}}
    <div class="mb-3">
        <label for="{{id}}" class="form-label">ID</label>
        <input readonly type="text" class="form-control" id="{{id}}" name="id" >
    </div>

    {{!-- X Field --}}
    <div class="mb-3">
        <label for="{{x}}" class="form-label">X</label>
        <input readonly type="text" class="form-control" id="{{x}}" name="x" >
    </div>

    {{!-- Y Field --}}
    <div class="mb-3">
        <label for="{{y}}" class="form-label">Y</label>
        <input readonly type="text" class="form-control" id="{{y}}" name="y" >
    </div>

    {{!-- Role Field (Dropdown) --}}
    <div class="mb-3">
        <label for="{{role}}" class="form-label">Role</label>
        <select class="form-select" id="{{role}}" name="role" >
            <option value="" disabled selected>Select a role</option>
            {{#each choices}}
            <option value="{{this.[0]}}">{{this.[1]}}</option>            
            {{/each}}
            

        </select>
    </div>

    {{!-- Submit Button --}}
    
</form>
`;