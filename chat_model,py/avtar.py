import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


VRM_PATH = Path(
    r"C:\Users\rites\Desktop\langchan model\chat_model,py\avatar.vrm"
)



def show_avatar():
    if not VRM_PATH.is_file():
        st.error(f"VRM file nahi mili: {VRM_PATH}")
        return

    try:
        with VRM_PATH.open("rb") as file:
            vrm_data = base64.b64encode(file.read()).decode("ascii")
    except OSError as error:
        st.error(f"VRM file read nahi ho saki: {error}")
        return

    # JSON encoding se base64 JavaScript string me safely inject hota hai.
    vrm_base64 = json.dumps(vrm_data)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
            html, body {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                background: #111111;
            }}

            #avatar-container {{
                position: relative;
                width: 100%;
                height: 100%;
                overflow: hidden;
                background: #111111;
            }}

            canvas {{
                display: block;
                width: 100%;
                height: 100%;
            }}

            #status {{
                position: absolute;
                top: 12px;
                left: 12px;
                right: 12px;
                padding: 8px 10px;
                color: white;
                background: rgba(0, 0, 0, 0.55);
                border-radius: 6px;
                font-family: Arial, sans-serif;
                font-size: 13px;
                z-index: 10;
            }}
        </style>

        <script type="importmap">
        {{
            "imports": {{
                "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
                "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/",
                "@pixiv/three-vrm": "https://cdn.jsdelivr.net/npm/@pixiv/three-vrm@3/lib/three-vrm.module.min.js"
            }}
        }}
        </script>
    </head>

    <body>
        <div id="avatar-container">
            <div id="status">Avatar loading...</div>
        </div>

        <script type="module">
            import * as THREE from "three";
            import {{ GLTFLoader }} from "three/addons/loaders/GLTFLoader.js";
            import {{
                VRMLoaderPlugin,
                VRMUtils
            }} from "@pixiv/three-vrm";

            const container = document.getElementById("avatar-container");
            const status = document.getElementById("status");

            function setStatus(message, isError = false) {{
                status.textContent = message;
                status.style.background = isError
                    ? "rgba(160, 0, 0, 0.75)"
                    : "rgba(0, 0, 0, 0.55)";
            }}

            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);

            const camera = new THREE.PerspectiveCamera(
                30,
                window.innerWidth / window.innerHeight,
                0.1,
                100
            );

            camera.position.set(0, 1.4, 4.5);

            const renderer = new THREE.WebGLRenderer({{
                antialias: true,
                alpha: false,
                powerPreference: "high-performance"
            }});

            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.outputColorSpace = THREE.SRGBColorSpace;
            container.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0xffffff, 2.2);
            scene.add(ambientLight);

            const keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
            keyLight.position.set(1, 3, 4);
            scene.add(keyLight);

            const fillLight = new THREE.DirectionalLight(0x99bbff, 1.0);
            fillLight.position.set(-2, 1, 2);
            scene.add(fillLight);

            let vrm = null;
            const clock = new THREE.Clock();

            function resizeRenderer() {{
                const width = container.clientWidth || window.innerWidth;
                const height = container.clientHeight || window.innerHeight;

                camera.aspect = width / height;
                camera.updateProjectionMatrix();

                renderer.setSize(width, height, false);
            }}

            function frameAvatar() {{
                if (!vrm) {{
                    return;
                }}

                const box = new THREE.Box3().setFromObject(vrm.scene);
                const size = box.getSize(new THREE.Vector3());
                const center = box.getCenter(new THREE.Vector3());

                const avatarHeight = Math.max(size.y, 1.0);
                const cameraDistance = Math.max(avatarHeight * 1.8, 2.4);

                camera.position.set(
                    center.x,
                    center.y + avatarHeight * 0.05,
                    center.z + cameraDistance
                );

                camera.lookAt(
                    center.x,
                    center.y + avatarHeight * 0.42,
                    center.z
                );
            }}

            const vrmBase64 = {vrm_base64};

            try {{
                const bytes = Uint8Array.from(
                    atob(vrmBase64),
                    character => character.charCodeAt(0)
                );

                const blob = new Blob(
                    [bytes],
                    {{ type: "application/octet-stream" }}
                );

                const modelUrl = URL.createObjectURL(blob);
                const loader = new GLTFLoader();

                loader.register((parser) => {{
                    return new VRMLoaderPlugin(parser);
                }});

                loader.load(
                    modelUrl,

                    (gltf) => {{
                        URL.revokeObjectURL(modelUrl);

                        vrm = gltf.userData.vrm;

                        if (!vrm) {{
                            setStatus(
                                "VRM load hua, lekin VRM object nahi mila.",
                                true
                            );
                            console.error("gltf.userData:", gltf.userData);
                            return;
                        }}

                        // VRM 0.0 models ke orientation ko correct karta hai.
                        VRMUtils.rotateVRM0(vrm);

                        vrm.scene.traverse((object) => {{
                            object.frustumCulled = false;
                        }});

                        scene.add(vrm.scene);
                        frameAvatar();

                        setStatus("Avatar loaded");
                        console.log("VRM loaded:", vrm);
                    }},

                    (progress) => {{
                        if (progress.total > 0) {{
                            const percent =
                                (progress.loaded / progress.total) * 100;

                            setStatus(
                                "Loading avatar " + percent.toFixed(0) + "%"
                            );
                        }} else {{
                            setStatus("Loading avatar...");
                        }}
                    }},

                    (error) => {{
                        URL.revokeObjectURL(modelUrl);

                        console.error("VRM loading error:", error);

                        const message = error && error.message
                            ? error.message
                            : String(error);

                        setStatus("VRM error: " + message, true);
                    }}
                );
            }} catch (error) {{
                console.error("Avatar setup error:", error);

                const message = error && error.message
                    ? error.message
                    : String(error);

                setStatus("Avatar setup error: " + message, true);
            }}

            function animate() {{
                requestAnimationFrame(animate);

                const delta = clock.getDelta();

                if (vrm) {{
                    vrm.update(delta);
                }}

                renderer.render(scene, camera);
            }}

            resizeRenderer();
            window.addEventListener("resize", () => {{
                resizeRenderer();
                frameAvatar();
            }});

            animate();
        </script>
    </body>
    </html>
    """

    components.html(
        html,
        height=650,
        scrolling=False
    )