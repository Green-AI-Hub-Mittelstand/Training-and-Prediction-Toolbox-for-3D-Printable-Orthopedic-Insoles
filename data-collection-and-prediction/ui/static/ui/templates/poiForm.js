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
                
                
                
                
                <button type="button" class="btn btn-light me-2 points " title="Punkte umstellen">
                    <i class="fa-solid fa-eye-slash"></i>
                </button>
            
                
              </div>
            
            
            
            
            
            


        </div>
        <div class="col">
            <div class="row">
                <div class="container">
                    
                </div>
                
                

                
                


                

















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
        <label for="{{role}}" class="form-label">Punkt Typ</label>
        <select disabled class="form-select" id="{{role}}" name="role" >
            <option value="" disabled selected>Punkt Typ auswählen</option>
            {{#each choices}}
            <option value="{{this.[0]}}">{{this.[1]}}</option>            
            {{/each}}
        </select>
    </div>

    {{!-- Submit Button --}}
    
</form>
`;