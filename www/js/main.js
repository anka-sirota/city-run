var camera, scene, renderer, controls, light, buildings_geometry, glowscene;
var ccolor = 0x0f0f1a;
var spec_ccolor = 0x0f0f1f;
var SCREEN_HEIGHT = window.innerHeight;
var SCREEN_WIDTH = window.innerWidth;
var manager = new THREE.LoadingManager();
manager.onProgress = function (item, loaded, total) {
    console.log('loaded', item, loaded, total);
};
var image_loader = new THREE.ImageLoader(manager);
var geometry_loader = new THREE.JSONLoader(manager);

function get_shader_text(url) {
    console.log('get_shader_text', url);
    var vtext;
    $.ajax({
        type: "GET",
        url: url,
        dataType: "text",
        async: false,
        timeout: 30000,
    }).done( function(text) {
        console.log(arguments);
        vtext = text;
    });
    return vtext;
}

function load_texture(url) {
    var t = new THREE.ImageUtils.loadTexture(url);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
}

function load_geometry(url) {
    var g = {g: undefined};
    geometry_loader.load(url, function(geometry) {
        console.log('load_geometry callback', arguments);
        geometry.scale = 10.0;
        geometry.computeTangents();
        g.g = geometry; // TODO
    });
    return g;
}

function init() {
    renderer = Detector.webgl ? new THREE.WebGLRenderer() : new THREE.CanvasRenderer();
    console.log(renderer);
    renderer.setSize(SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.8);
    renderer.setClearColor(ccolor, 1);
    renderer.autoClear = false;
    renderer.sortObjects = true;
	renderer.domElement.style.position = "relative";
    document.body.appendChild(renderer.domElement );

    camera = new THREE.PerspectiveCamera( 75, SCREEN_WIDTH / SCREEN_HEIGHT, 1, 1000 );
    
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(ccolor, 0.010);

    light = new THREE.DirectionalLight(0xaa99bb, 0.5);
    light.position.set(500, 500, 1500);
    light.castShadow = true;
    scene.add(light);
    var ambientLight = new THREE.AmbientLight(ccolor);
    scene.add(ambientLight);

    //camera control properties
    controls = new THREE.FlyControls(camera);
    controls.movementSpeed = 1;
    controls.domElement = document;
    controls.rollSpeed = 0.01;
    controls.autoForward = false;
    controls.dragToLook = true;

    // GLOW SCENE
    glowscene = new THREE.Scene();
    glowscene.add(new THREE.AmbientLight(0xffffff));
    glowscene.add(new THREE.AmbientLight(0xffffff));
    glowscene.add(new THREE.AmbientLight(0xffffff));
    glowscene.fog = new THREE.FogExp2(ccolor, 0.008);
    glowcamera = new THREE.PerspectiveCamera( 75, SCREEN_WIDTH / SCREEN_HEIGHT, 1, 1000 );
    glowcamera.position = camera.position;
}

function animate() {
    requestAnimationFrame(animate);
    //renderer.render(glowscene, camera);
    controls.update(1);
    glowcomposer.render();
    finalcomposer.render();
}


var buildings = load_geometry('/static/buildings.js');
var tDiffuse = load_texture('/static/Needlepoint_Steel.png');
var tNormal = load_texture('/static/Needlepoint_Steel_Normal_Map.png');
var tSpecular = load_texture('/static/build0_spec_col.png');
var tSpecularGlow = load_texture('/static/build0_spec_col_glow.png');

init();

function setup_material() {
    var geometry = buildings;
    var shader = THREE.ShaderLib["normalmap_"];

    var uniforms = THREE.UniformsUtils.clone(shader.uniforms);
    uniforms["tNormal"].value = tNormal;
    uniforms["offsetRepeatNormal"].value.set(0, 0, 40, 40);
    uniforms["uNormalScale"].value.set(5.0, 5.0);

    uniforms["tDiffuse"].value = tDiffuse;
    uniforms["offsetRepeatDiffuse"].value.set(0, 0, 40, 40);
    uniforms["enableDiffuse" ].value = true;

    uniforms["tSpecular"].value = tSpecular;
    uniforms["offsetRepeatSpecular"].value.set(0, 0, 1, 1);
    uniforms["specular"].value.setHex(spec_ccolor);
    uniforms["enableSpecular" ].value = true;
    uniforms["shininess"].value = 200;
    uniforms["useRefract" ].value = true;

    console.log(shader);

    var parameters = {fragmentShader: shader.fragmentShader, vertexShader: shader.vertexShader, uniforms: uniforms, lights: true, fog: true};
    var material = new THREE.ShaderMaterial(parameters);
    material.wrapAround = true;

    mesh = new THREE.Mesh(geometry, material);
    mesh.updateMatrix();
    mesh.overdraw = true;
    mesh.receiveShadow = true;
    mesh.castShadow = true;
    scene.add(mesh);

    var gmat = new THREE.MeshPhongMaterial( { map: tSpecularGlow, ambient: 0xffffff, color: 0x000000 } );
    // Create mesh with the glow material
    var gmesh = new THREE.Mesh(geometry, gmat);
    // Map cloned mesh properties to base mesh
    gmesh.updateMatrix();
    gmesh.position = mesh.position;
    gmesh.scale = mesh.scale;
    gmesh.overdraw = true;
 
    // Add the cloned mesh to the glow scene
    glowscene.add(gmesh);

    // Prepare the glow composer's render target
    var renderTargetParameters = { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, format: THREE.RGBFormat, stencilBufer: false };
    renderTargetGlow = new THREE.WebGLRenderTarget( SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.8, renderTargetParameters );
     
    // Prepare the blur shader passes
    hblur = new THREE.ShaderPass( THREE.HorizontalBlurShader );
    vblur = new THREE.ShaderPass( THREE.VerticalBlurShader );
     
    var bluriness = 0.5; 
     
    hblur.uniforms[ "h" ].value = bluriness / (SCREEN_WIDTH * 0.8);
    vblur.uniforms[ "v" ].value = bluriness / (SCREEN_HEIGHT * 0.8);
     
    // Prepare the glow scene render pass
    var renderModelGlow = new THREE.RenderPass( glowscene, camera);
     
    // Create the glow composer
    glowcomposer = new THREE.EffectComposer( renderer, renderTargetGlow );
     
    // Add all the glow passes
    glowcomposer.addPass(renderModelGlow );
    glowcomposer.addPass(hblur);
    glowcomposer.addPass(vblur);

    var finalshader = {
    uniforms: {
        tDiffuse: { type: "t", value: 0, texture: null }, // The base scene buffer
        tGlow: { type: "t", value: 1, texture: null } // The glow scene buffer
    },
 
    vertexShader: [
        "varying vec2 vUv;",
        "void main() {",
            "vUv = uv;",
            "gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );",
        "}"
    ].join("\n"),
 
    fragmentShader: [
        "uniform sampler2D tDiffuse;",
        "uniform sampler2D tGlow;",
        "varying vec2 vUv;",
        "void main() {",
            "vec4 texel = texture2D( tDiffuse, vUv );",
            "vec4 glow = texture2D( tGlow, vUv );",
            "gl_FragColor = texel + vec4(0.5, 0.75, 1.0, 1.0) * glow * 2.0;", 
        "}"
    ].join("\n")
    };

    // First we need to assign the glow composer's output render target to the tGlow sampler2D of our shader
    // New Three.js
    finalshader.uniforms[ "tGlow" ].value = glowcomposer.renderTarget2;
    // Note that the tDiffuse sampler2D will be automatically filled by the EffectComposer
     
    // Prepare the base scene render pass
    var renderModel = new THREE.RenderPass( scene, camera );
     
    // Prepare the additive blending pass
    var finalPass = new THREE.ShaderPass( finalshader );
    finalPass.needsSwap = true;
     
    // Make sure the additive blending is rendered to the screen (since it's the last pass)
    finalPass.renderToScreen = true;
     
    // Prepare the composer's render target
    renderTarget = new THREE.WebGLRenderTarget( SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.8, renderTargetParameters );
     
    // Create the composer
    finalcomposer = new THREE.EffectComposer( renderer, renderTarget );
     
    // Add all passes
    finalcomposer.addPass( renderModel );
    finalcomposer.addPass( finalPass );
}

function wait_for(el) {
    if (!tDiffuse || !tNormal || !tSpecular || !tSpecularGlow || !buildings.g) { // TODO
        console.log('waiting still');
        setTimeout(function() { wait_for(el) }, 300);
    }
    else {
        console.log('ready', tDiffuse, tNormal, tSpecular, buildings);
        buildings = buildings.g; // OH GOD NO. TODO
        setup_material();
        animate();
    }
}

wait_for();
