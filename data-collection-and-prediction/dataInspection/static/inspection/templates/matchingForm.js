var matchingForm = `

<div class="btn-toolbar" role="toolbar" style="margin-bottom:3px">
    <!-- Undo Button -->
    <button type="button" class="btn btn-light me-2 reset" title="Undo">
        <i class="fas fa-undo"></i>
    </button>
    <!-- Redo Button -->
    <button type="button" class="btn btn-light me-2 save" title="Save">
        <i class="fas fa-save"></i>
    </button>
  </div>


  
  
  <div class="btn-toolbar" role="toolbar"  style="margin-bottom:3px">
    
    
    <button type="button" class="btn btn-light me-2 toggleView" title="Kontrast umschalten" title="Kontrast umschalten">
        <i class="fa-solid fa-circle-half-stroke"></i>
    </button>

    <button type="button" class="btn btn-light me-2 togglePressureView" title="Druckbild umschalten">
        <i class="fa-solid fa-eye-slash"></i>
    </button>

    
    <button type="button" class="btn btn-light me-2 copy " title="Auf andere Kopieren">
        <i class="fa-solid fa-copy"></i>
    </button>

    
  </div>

  Kontrast<br>
  <input type="range" min="1" max="10" value="20" class="contrast-slider" >
  <span class="current-contrast"></span><br>
  <br>
  
  Helligkeit<br>  
  <input type="range" min="1" max="20" value="20" class="brightness-slider" ><span class="current-brightness"></span><br>


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
        <label for="{{rot}}" class="form-label">Rotation</label>
        <input readonly type="text" class="form-control" id="{{rot}}" name="rot" >
    </div>

    {{!-- Quality Field (Dropdown) --}}
    <div class="mb-3">
        <label for="{{quality}}" class="form-label">Quality</label>
        <select class="form-control" id="{{quality}}">
            <option value="0">schlecht</option>
            <option value="1">mittel</option>
            <option value="2">gut</option>

        </select>

        
    </div>

    {{!-- Submit Button --}}
    
</form>

`;