/* global THREE */

(function () {

  /* ------------------------------------------
     reduce motion support
  ------------------------------------------ */
  function prefersReducedMotion() {
    return (
      window.matchMedia &&
      window.matchMedia(
        "(prefers-reduced-motion: reduce)"
      ).matches
    );
  }


  /* ------------------------------------------
     clamp helper
  ------------------------------------------ */
  function clamp(
    value,
    min,
    max
  ) {
    return Math.min(
      Math.max(value, min),
      max
    );
  }


  /* ------------------------------------------
     create canvas renderer
  ------------------------------------------ */
  function createRenderer() {

    const canvas =
      document.createElement(
        "canvas"
      );

    canvas.className =
      "three-bg";

    document.body.prepend(
      canvas
    );

    const renderer =
      new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: true,
        powerPreference:
          "high-performance"
      });

    renderer.setPixelRatio(
      Math.min(
        window.devicePixelRatio || 1,
        2
      )
    );

    renderer.setClearColor(
      0x000000,
      0
    );

    return renderer;
  }


  /* ------------------------------------------
     create scene
  ------------------------------------------ */
  function createScene() {

    const scene =
      new THREE.Scene();

    scene.fog =
      new THREE.FogExp2(
        0x0b1020,
        0.055
      );

    return scene;
  }


  /* ------------------------------------------
     camera
  ------------------------------------------ */
  function createCamera() {

    const camera =
      new THREE.PerspectiveCamera(
        55,
        1,
        0.1,
        200
      );

    camera.position.set(
      0,
      0.4,
      10
    );

    return camera;
  }


  /* ------------------------------------------
     lighting
  ------------------------------------------ */
  function addLights(scene) {

    const ambient =
      new THREE.AmbientLight(
        0xffffff,
        0.40
      );

    scene.add(ambient);

    const keyLight =
      new THREE.DirectionalLight(
        0xa78bfa,
        1
      );

    keyLight.position.set(
      6,
      8,
      4
    );

    scene.add(keyLight);

    const rimLight =
      new THREE.DirectionalLight(
        0xd946ef,
        0.75
      );

    rimLight.position.set(
        -6,
        -2,
        6
    );

    scene.add(rimLight);
  }


  /* ------------------------------------------
     center object
  ------------------------------------------ */
  function addMainObject(
    scene
  ) {

    const geometry =
      new THREE.TorusKnotGeometry(
        2.4,
        0.7,
        180,
        24
      );

    const material =
      new THREE.MeshPhysicalMaterial({
        color: 0x8b5cf6,
        roughness: 0.22,
        metalness: 0.18,
        transmission: 0.58,
        thickness: 0.8,
        clearcoat: 0.7,
        clearcoatRoughness: 0.2
      });

    const mesh =
      new THREE.Mesh(
        geometry,
        material
      );

    mesh.position.set(
      0,
      0.1,
      -2.5
    );

    scene.add(mesh);

    return mesh;
  }


  /* ------------------------------------------
     stars
  ------------------------------------------ */
  function addStars(
    scene,
    count = 800
  ) {

    const geometry =
      new THREE.BufferGeometry();

    const positions =
      new Float32Array(
        count * 3
      );

    for (
      let i = 0;
      i < count;
      i++
    ) {

      const i3 = i * 3;

      positions[i3] =
        (Math.random() - 0.5) * 40;

      positions[i3 + 1] =
        (Math.random() - 0.5) * 24;

      positions[i3 + 2] =
        -Math.random() * 50;
    }

    geometry.setAttribute(
      "position",
      new THREE.BufferAttribute(
        positions,
        3
      )
    );

    const material =
      new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.06,
        opacity: 0.8,
        transparent: true,
        depthWrite: false
      });

    const stars =
      new THREE.Points(
        geometry,
        material
      );

    scene.add(stars);

    return stars;
  }


  /* ------------------------------------------
     resize
  ------------------------------------------ */
  function resize(
    renderer,
    camera
  ) {

    const width =
      Math.max(
        1,
        window.innerWidth
      );

    const height =
      Math.max(
        1,
        window.innerHeight
      );

    renderer.setSize(
      width,
      height,
      false
    );

    camera.aspect =
      width / height;

    camera.updateProjectionMatrix();
  }


  /* ------------------------------------------
     main start
  ------------------------------------------ */
  function start() {

    if (!window.THREE) return;

    if (
      prefersReducedMotion()
    ) return;

    if (
      document.querySelector(
        "canvas.three-bg"
      )
    ) return;

    const renderer =
      createRenderer();

    const scene =
      createScene();

    const camera =
      createCamera();

    addLights(scene);

    const object3D =
      addMainObject(scene);

    const stars =
      addStars(
        scene,
        900
      );

    let mouseX = 0;
    let mouseY = 0;

    window.addEventListener(
      "mousemove",
      function (event) {

        mouseX =
          (event.clientX /
            window.innerWidth) *
            2 -
          1;

        mouseY =
          (event.clientY /
            window.innerHeight) *
            2 -
          1;
      },
      { passive: true }
    );


    function onResize() {
      resize(
        renderer,
        camera
      );
    }

    window.addEventListener(
      "resize",
      onResize,
      { passive: true }
    );

    onResize();

    const clock =
      new THREE.Clock();


    /* ------------------------------------------
       animation loop
    ------------------------------------------ */
    function animate() {

      const t =
        clock.getElapsedTime();

      camera.position.x =
        clamp(
          mouseX * 0.6,
          -1.1,
          1.1
        );

      camera.position.y =
        0.4 +
        clamp(
          -mouseY * 0.25,
          -0.35,
          0.35
        );

      camera.lookAt(
        0,
        0.1,
        0
      );

      object3D.rotation.x =
        t * 0.22;

      object3D.rotation.y =
        t * 0.28;

      object3D.position.y =
        0.1 +
        Math.sin(
          t * 0.8
        ) * 0.12;

      stars.rotation.y =
        t * 0.02;

      renderer.render(
        scene,
        camera
      );

      requestAnimationFrame(
        animate
      );
    }

    requestAnimationFrame(
      animate
    );
  }


  window.addEventListener(
    "DOMContentLoaded",
    start
  );

})();