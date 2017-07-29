var Canvas3DModule = function(canvas_width, canvas_height, grid_width, grid_height, flip_y) {

    // TODO - determine how to allow grass patches to be grown in the base layer, instead of as cubes.
    // Perhaps allow it to be determined by the portrayal method, 'cube' vs 'plane'?

    // scene bounds
    this.width = grid_width;
    this.height = grid_height;
    this.right = grid_width / 2;
    this.left = grid_width / 2 * -1;
    this.bottom = grid_height / 2;
    this.top = grid_height / 2 * -1;
    this.offset = 0.1;
    this.flip_y = flip_y;

    var self = this;

	// Create the tag:
	var tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
	tag += "style='border:1px dotted'></canvas>";
	// Append it to body:
	var canvas = $(tag)[0];
	$("#elements").append(canvas);


	// First time setup
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera( 75, canvas_width / canvas_height, 0.1, 1000 );
    camera.up = new THREE.Vector3(0, 0, 1);
    var renderer = new THREE.WebGLRenderer({canvas: canvas});
    var controls = new THREE.OrbitControls(camera, renderer.domElement);
    renderer.setSize(canvas_width, canvas_height);

    var colorPlane = new THREE.PlaneGeometry(grid_width, grid_height, grid_width, grid_height);
    var material = new THREE.MeshBasicMaterial({color: 'white', side: THREE.DoubleSide});
    var mesh = new THREE.Mesh( colorPlane, material );
    scene.add( mesh );
    camera.position.z = (grid_height + grid_width) / 2;

    var animate = function () {
        requestAnimationFrame( animate );
        controls.update();
        renderer.render(scene, camera);
    };

    var textureLoader = new THREE.TextureLoader();

    animate();  // Start rendering as soon as we're ready

    var cubeLayers = {
        portrayals: [],
        materials: {}
    };

    var planeLayers = {};   // Todo - portrayal method?

    var updateCubeLayer = function(layer, portrayalLayer, portrayalShape) {
        if (["rect", "circle", "arrowHead"].indexOf(portrayalShape) < 0) {
            textureLoader.load('local/'.concat(portrayalShape), function(texture) {
                cubeLayers.materials[layer] = new THREE.MeshBasicMaterial({map: texture});
                makeCubes(layer, portrayalLayer);
            })
        }
        else if (portrayalLayer[0].hasOwnProperty('Color')) {
            var color = portrayalLayer[0].Color;
            cubeLayers.materials[layer] = new THREE.MeshBasicMaterial({color: color});
            makeCubes(layer, portrayalLayer);
        } else {
            console.log("Couldn't determine shape, skipping layer {}.".replace('{}', String(layer)));
        }
    };

    var removeCubes = function(layer) {
        scene.remove(scene.getObjectByName(layer));
    };

    var makeCubes = function(layer, layerData) {

        // Time to make some cubes!
        var group = new THREE.Group();
        group.name = layer;

        var makeOneCube = function(data) {
            var mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), cubeLayers.materials[layer]);
            mesh.userData = data;
            group.add(mesh);
            mesh.position.copy(
                new THREE.Vector3( -self.width/2 + data.x, -self.height / 2 + data.y, 0.5 + self.offset)
            );
            if (self.flip_y) {
                mesh.position.y = self.height / 2 - data.y;
            }
            console.log(data.x, data.y);
            mesh.updateMatrix();
        };

        // Grid starts in bottom left of scene
        for (var c in layerData) {
            var data = layerData[c];
            makeOneCube(data);
        }

        scene.add(group);
    };

	this.render = function(data) {

	    // Go through each layer of the portrayal, decide if we've seen it before.
        // The number of unique portrays in a given instance may change
        for (var layer in data) {
            if (!cubeLayers.portrayals.includes(layer)) {
                cubeLayers.portrayals.push(layer);
                updateCubeLayer(layer, data[layer], data[layer][0].Shape, makeCubes);
            }
            else {
                removeCubes(layer);             // need to remove cubes for a layer that currently exists.
                makeCubes(layer, data[layer]);
            }
        }
	};

    this.reset = function() {
        // Reset camera position
        camera.position.copy(new THREE.Vector3(0, 0, (grid_width + grid_height) / 2));
        camera.matrix.needsUpdate();
    }
};
