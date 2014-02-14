var camera, scene, renderer, controls, light, buildings_geometry;
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

function load_texture(url, repeat) {
    var t = new THREE.Texture();
    image_loader.load(url, function (image) {
        t.image = image;
        t.needsUpdate = true;
        t.repeat.set(repeat, repeat);
        t.wrapS = t.wrapT = THREE.RepeatWrapping;
    } );
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
    renderer.setSize(window.innerWidth / 2, window.innerHeight / 2);
    renderer.setClearColor(0x000072, 1);
    document.body.appendChild(renderer.domElement );

    camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 1000 );
    scene = new THREE.Scene();
    light = new THREE.DirectionalLight(0xffffff, 1);

    light.position.set(10, 5, 10);
    light.castShadow = true;
    scene.add(light);

    //camera control properties
    controls = new THREE.FlyControls(camera);
    controls.movementSpeed = 1;
    controls.domElement = document;
    controls.rollSpeed = 0.01;
    controls.autoForward = false;
    controls.dragToLook = true;
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
    controls.update(1);
}


var buildings = load_geometry('/static/buildings.js');
var tDiffuse = load_texture('/static/Needlepoint_Steel.png', 90);
var tNormal = load_texture('/static/Needlepoint_Steel_Normal_Map.png', 90);
var tSpecular = load_texture('/static/build0_spec.png', 1);

init();

function setup_material() {
    var geometry = buildings;
    var shader = THREE.ShaderLib["normalmap"];

    var uniforms = THREE.UniformsUtils.clone(shader.uniforms);
    console.log(uniforms);
    uniforms["tNormal"].value = tNormal;

    uniforms["tDiffuse"].value = tDiffuse;
    uniforms["enableDiffuse" ].value = true;

    uniforms["tSpecular"].value = tSpecular;
    uniforms["specular"].value.setHex(0x060606);
    uniforms["enableSpecular" ].value = true;
    uniforms["shininess"].value = 100;

    //uniforms["uRepeat"].value.set(10, 10);
    uniforms["enableAO"].value = false;

    var parameters = {fragmentShader: shader.fragmentShader, vertexShader: shader.vertexShader, uniforms: uniforms, lights: true, fog: false};
    var material = new THREE.ShaderMaterial(parameters);
    material.wrapAround = true;

    mesh = new THREE.Mesh(geometry, material);
    mesh.updateMatrix();
    mesh.overdraw = true;
    mesh.receiveShadow = true;
    mesh.castShadow = true;
    scene.add(mesh);
}

function wait_for(el) {
    if (!tDiffuse || !tNormal || !tSpecular || !buildings.g) { // TODO
        console.log('waiting still');
        setTimeout(function() { wait_for(el) }, 100);
    }
    else {
        console.log('ready', tDiffuse, tNormal, tSpecular, buildings);
        buildings = buildings.g; // OH GOD NO. TODO
        setup_material();
        animate();
    }
}

wait_for();
