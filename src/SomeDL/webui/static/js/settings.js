document.querySelectorAll(".settings-help-btn").forEach((node) => {    
    node.addEventListener("click", () => {
        node.parentNode.querySelector(".popup-box").style.display = "flex"
    })
})

document.querySelectorAll(".popup-box").forEach((node) => {    
    node.addEventListener("click", (e) => {      
        if (e.target !== e.currentTarget && !e.target.matches('.popup-close, .popup-exit')) return;
        node.style.display = "none"
    });
})

document.querySelectorAll(".s-inp").forEach(input => {
    input.addEventListener("change", () => {
        document.querySelectorAll(".settings-reset").forEach(el => {
            el.classList.remove("disabled");
        });
        document.querySelectorAll(".settings-apply").forEach(el => {
            el.classList.remove("disabled");
        });
        document.querySelectorAll(".settings-save").forEach(el => {
            el.classList.remove("disabled");
        });
    });
});


document.querySelectorAll("input[name='webui-theme-type-selector']").forEach(el => {
    el.addEventListener("change", () => {
        if (el.value == "light") {
            document.querySelectorAll(".s-webui-color-theme-dark").forEach(el => el.style.display = "none");
            document.querySelectorAll(".s-webui-color-theme-light").forEach(el => el.style.display = "flex");
        } else if (el.value == "dark") {
            document.querySelectorAll(".s-webui-color-theme-dark").forEach(el => el.style.display = "flex");
            document.querySelectorAll(".s-webui-color-theme-light").forEach(el => el.style.display = "none");
        } else {
            document.querySelectorAll(".s-webui-color-theme-dark").forEach(el => el.style.display = "flex");
            document.querySelectorAll(".s-webui-color-theme-light").forEach(el => el.style.display = "flex");
        }
        
    })
});


var settings = {
    default: {
        "api": {
            "musicbrainz": true,
            "genius": true,
            "genius_album_check": true,
            "deezer": true,
            "max_retry": 3
        },
        "metadata": {
            "lyrics": true,
            "copyright": true,
            "isrc": true,
            "genre": true,
            "album_artist": true,
            "multiple_artists": false,
            "artist_separator": "; ",
            "ffmpeg_metadata": false,
            "cover_art_file": false,
            "cover_art_size": "l",
            "lyrics_type": "plain",
            "synced_lyrics_metadata": true,
            "lrc_file": false,
            "lyrics_id3_synced_uslt_fallback": false,
            "lyrics_source": "lrclib",
            "lyrics_fallback_source": "youtube"
        },
        "download": {
            "format": "mp3",
            "quality": 5,
            "id3_version": 3,
            "output_dir": ".",
            "output": "{artist} - {song}",
            "number_downloaders": 2,
            "queue_size": 2,
            "sleep": 0,
            "cookies_path": "",
            "cookies_from_browser": "",
            "prefer_playlist": false,
            "fetch_albums": false,
            "check_if_file_exists": true,
            "download_archive": "",
            "sync_files": []
        },
        "logging": {
            "log_level": 4,
            "download_report": 2
        },
        "webui": {
            "host": "127.0.0.1",
            "port": "5000",
        }
    },
    current: {},
    webui_preset_themes: {
        "SomeDL": {
            "predefined": true,
            "theme": "light",
            "color-main": "#ad3013",
            "color-main-highlight": "#d2360f",
            "color-background": "#808080",
            "color-background-highlight": "#979797",
            "color-button": "#666666",
            "color-border": "#d3d3d3",
            "color-text": "#FFFFFF",
        },
        "SomeDL Dark": {
            "predefined": true,
            "theme": "dark",
            "color-main": "#802511",
            "color-main-highlight": "#ac3011",
            "color-background": "#1e1c20",
            "color-background-highlight": "#2d2b2f",
            "color-button": "#0f0f0f",
            "color-border": "#767676",
            "color-text": "#FFFFFF",
        },
        "Emerald": {
            "predefined": true,
            "theme": "light",
            "color-main": "#114921",
            "color-main-highlight": "#27733c",
            "color-background": "#808080",
            "color-background-highlight": "#979797",
            "color-button": "#666666",
            "color-border": "#d3d3d3",
            "color-text": "#FFFFFF",
        },
        "Emerald Dark": {
            "predefined": true,
            "theme": "dark",
            "color-main": "#114921",
            "color-main-highlight": "#27733c",
            "color-background": "#1e1c20",
            "color-background-highlight": "#2d2b2f",
            "color-button": "#0f0f0f",
            "color-border": "#767676",
            "color-text": "#FFFFFF",
        },
        "Amethyst": {
            "predefined": true,
            "theme": "light",
            "color-main": "#5744b5",
            "color-main-highlight": "#705fc2",
            "color-background": "#808080",
            "color-background-highlight": "#979797",
            "color-button": "#666666",
            "color-border": "#d3d3d3",
            "color-text": "#FFFFFF",
        },
        "Amethyst Dark": {
            "predefined": true,
            "theme": "dark",
            "color-main": "#5744b5",
            "color-main-highlight": "#705fc2",
            "color-background": "#1e1c20",
            "color-background-highlight": "#2d2b2f",
            "color-button": "#0f0f0f",
            "color-border": "#767676",
            "color-text": "#FFFFFF",
        },
        "Turquoise": {
            "predefined": true,
            "theme": "light",
            "color-main": "#005f6a",
            "color-main-highlight": "#0b6873",
            "color-background": "#808080",
            "color-background-highlight": "#979797",
            "color-button": "#666666",
            "color-border": "#d3d3d3",
            "color-text": "#FFFFFF",
        },
        "Turquoise Dark": {
            "predefined": true,
            "theme": "dark",
            "color-main": "#005f6a",
            "color-main-highlight": "#0b6873",
            "color-background": "#1e1c20",
            "color-background-highlight": "#2d2b2f",
            "color-button": "#0f0f0f",
            "color-border": "#767676",
            "color-text": "#FFFFFF",
        },
        "Ruby": {
            "predefined": true,
            "theme": "light",
            "color-main": "#a71010",
            "color-main-highlight": "#c02f2f",
            "color-background": "#808080",
            "color-background-highlight": "#979797",
            "color-button": "#666666",
            "color-border": "#d3d3d3",
            "color-text": "#FFFFFF",
        },
        "Ruby Dark": {
            "predefined": true,
            "theme": "dark",
            "color-main": "#610505",
            "color-main-highlight": "#6f1414",
            "color-background": "#1e1c20",
            "color-background-highlight": "#2d2b2f",
            "color-button": "#0f0f0f",
            "color-border": "#767676",
            "color-text": "#FFFFFF",
        },
        "Sapphire": {
            "predefined": true,
            "theme": "light",
            "color-main": "#12086b",
            "color-main-highlight": "#1f1487",
            "color-background": "#808080",
            "color-background-highlight": "#979797",
            "color-button": "#666666",
            "color-border": "#d3d3d3",
            "color-text": "#FFFFFF",
        },
        "Sapphire Dark": {
            "predefined": true,
            "theme": "dark",
            "color-main": "#12086b",
            "color-main-highlight": "#1f1487",
            "color-background": "#1e1c20",
            "color-background-highlight": "#2d2b2f",
            "color-button": "#0f0f0f",
            "color-border": "#767676",
            "color-text": "#FFFFFF",
        },
        "Coal": {
            "predefined": true,
            "theme": "light",
            "color-main": "#131213",
            "color-main-highlight": "#262526",
            "color-background": "#808080",
            "color-background-highlight": "#979797",
            "color-button": "#666666",
            "color-border": "#d3d3d3",
            "color-text": "#FFFFFF",
        },
        "Coal Dark": {
            "predefined": true,
            "theme": "dark",
            "color-main": "#131213",
            "color-main-highlight": "#262526",
            "color-background": "#1e1c20",
            "color-background-highlight": "#2d2b2f",
            "color-button": "#0f0f0f",
            "color-border": "#767676",
            "color-text": "#FFFFFF",
        },
    },
    webui_settings: {
        active_theme: "SomeDL Dark",
        custom_themes: {}
    },
    read () {
        // --- Read configs from html
        settings_elements = document.querySelectorAll(".s-inp")
        var new_config = {"api": {}, "metadata": {}, "download": {}, "logging": {}, "webui": {}};

        for (let i = 0; i < settings_elements.length; i++) {
            const element = settings_elements[i];
            const id = element.id.replace("s-", "");
            const group = element.classList[1].replace("s-", ""); // --- IMPORTANT: group name has to always be the second class name!
            
            if (id == "sync_files") {
                sync_files = element.value.trim() === "" ? [] : element.value.split(",").map(s => s.trim());
                new_config[group][id] = sync_files;
                continue;
            }
            
            if (element.type == "checkbox") {
                new_config[group][id] = element.checked;
            } else {
                var num = element.value == "" ? "" : Number(element.value);
                new_config[group][id] = isNaN(num) ? element.value : num;
            }
        }

        return new_config;
    },
    set (config) {
        // --- Set the HTML configs; only use internally for code deduplication
        settings_elements = document.querySelectorAll(".s-inp")
        for (let i = 0; i < settings_elements.length; i++) {
            const element = settings_elements[i];
            const id = element.id.replace("s-", "");
            const group = element.classList[1].replace("s-", ""); // --- IMPORTANT: group name has to always be the second class name!
            
            if (id == "sync_files") {
                element.value = config[group][id].join(", ")
                continue;
            }
            
            if (element.type == "checkbox") {
                element.checked = config[group][id]
            } else {
                element.value = config[group][id]
            }
            element.dispatchEvent(new Event('input', { bubbles: true }))}
    },
    remember_current () {
        // --- Store the configs from HTML to this.current
        console.log(" === Settings remember current === ");
        this.current = this.read()
    },
    prompt_set_defaults () {
        alert_box("Attention!", `
            <p>Do you want to revert all settings to the default values?</p>
            <p>Don't forget to save the changes!</p>
            <div class="popup-button-box">
                <button class="ui-button ui-button-small popup-exit"" onclick="settings.set_defaults()">OK</button>
                <button class="ui-button ui-button-small popup-exit">Cancel</button>
            </div>  
        `);
    },
    prompt_apply () {
        alert_box("Do you want to apply changes?", `
            <p>Do you want to save these changes to the config file AND update your current session configuration?</p>
            <p><i>Be aware that changing certain settings on a running download may result in failed downloads. Also, certain settings require a complete restart of the application (e.g. number of concurrent downloaders). Please restart the application if there are problems.<i></p>
            <div class="popup-button-box">
                <button class="ui-button ui-button-small popup-exit"" onclick="settings.apply()">OK</button>
                <button class="ui-button ui-button-small popup-exit">Cancel</button>
            </div>  
        `);
    },
    prompt_save () {
        alert_box("Do you want to save changes?", `
            <p>Do you want to save these changes to the config file?</p>
            <p><i>ATTENTION: The settings only take effect after restarting the application! Use "Apply" if you want to update the settings of the current session.<i></p>
            <div class="popup-button-box">
                <button class="ui-button ui-button-small popup-exit"" onclick="settings.apply()">OK</button>
                <button class="ui-button ui-button-small popup-exit">Cancel</button>
            </div>  
        `);
    },
    async set_defaults () {
        // TODO Gather defaults from server or use them from variable?
        console.log(" === Set defaults === ");
        this.set(this.default)
        document.querySelectorAll(".settings-reset").forEach(el => {
            el.classList.remove("disabled");
        });
        document.querySelectorAll(".settings-apply").forEach(el => {
            el.classList.remove("disabled");
        });
        document.querySelectorAll(".settings-save").forEach(el => {
            el.classList.remove("disabled");
        });
    },
    reset () {
        this.set(this.current)
        document.querySelectorAll(".settings-reset").forEach(el => {
            el.classList.add("disabled");
        });
        document.querySelectorAll(".settings-apply").forEach(el => {
            el.classList.add("disabled");
        });
        document.querySelectorAll(".settings-save").forEach(el => {
            el.classList.add("disabled");
        });
    },
    async load () {
        const loaded_settings = await settings_read()
        this.set(loaded_settings)
    },
    async apply () {
        // --- Updates config file & loaded configs
        console.log(" === Settings apply === ");

        // if (!confirm("Changing the settings of a running session may lead to some of the running downloads failing. Do you want to continue?")) {
        //     return;
        // }

        await settings_apply(this.read(), true);
        settings.remember_current();

        document.querySelectorAll(".settings-reset").forEach(el => {
            el.classList.add("disabled");
        });
        document.querySelectorAll(".settings-apply").forEach(el => {
            el.classList.add("disabled");
        });
        document.querySelectorAll(".settings-save").forEach(el => {
            el.classList.add("disabled");
        });

    },
    async save () {
        // --- Updates only config file, changes take effect only after reload
        console.log(" === Settings save === ");

        await settings_apply(this.read(), false);
        settings.remember_current();

        document.querySelectorAll(".settings-reset").forEach(el => {
            el.classList.add("disabled");
        });
        document.querySelectorAll(".settings-save").forEach(el => {
            el.classList.add("disabled");
        });

    },

    init_webui_appearance (theme_list) {
        var settings_field = document.getElementById("settings-webui")
        var field_content = settings_field.innerHTML;
        for (const [key, value] of Object.entries(theme_list)) {
            var id = "s-webui-id-" + key.replaceAll(" ", "-")
            field_content += `
            <label id="${id}" class="s-webui-color-wrap s-webui-color-theme-${value.theme}">
                <input type="radio" name="webui-color" onchange="settings.webui_update('${key}')"/>
                <div class="s-webui-color-title" data-theme="${value.theme}">${key}</div>
                <div class="s-webui-color-boxes">
                    <div class="s-webui-inp-color-main" style="background-color: ${value['color-main']};"></div>
                    <div class="s-webui-inp-color-main-highlight" style="background-color: ${value['color-main-highlight']};"></div>
                    <div class="s-webui-inp-color-background" style="background-color: ${value['color-background']};"><span class="s-webui-inp-color-text" style="color: ${value['color-text']};">Text</span></div>
                    <div class="s-webui-inp-color-background-highlight" style="background-color: ${value['color-background-highlight']};"></div>
                    <div class="s-webui-inp-color-button" style="background-color: ${value['color-button']};"></div>
                    <div class="s-webui-inp-color-border" style="background-color: ${value['color-border']};"></div>
                </div>`
            
            if (value.predefined) {
                field_content += `<div class="s-webui-noicon"></div><div class="s-webui-noicon"></div></label>`
                field_content += `<div class="s-webui-noicon"></div><div class="s-webui-noicon"></div></label>`
                continue;
            }
            field_content += `
                <div class="s-webui-edit" onclick="settings.prompt_webui_edit_theme('${key}')">${icons.edit}</div>
                <div class="s-webui-trash" onclick="settings.prompt_webui_delete_theme('${key}')">${icons.trash}</div>
            </label>`
        }

        settings_field.innerHTML = field_content;

    },
    webui_update (theme_name) {
        var current_settings = this.webui_preset_themes[theme_name];
        if (!current_settings) {
            current_settings = this.webui_settings.custom_themes[theme_name];
        }
        this.webui_settings.active_theme = theme_name;

        var key = "s-webui-id-" + theme_name.replaceAll(" ", "-");
        document.getElementById(key).querySelector("input[type='radio']").checked = true;

        document.documentElement.style.setProperty('--theme',                       current_settings["theme"])
        document.documentElement.style.setProperty('--color-main',                  current_settings["color-main"])
        document.documentElement.style.setProperty('--color-main-highlight',        current_settings["color-main-highlight"])
        document.documentElement.style.setProperty('--color-background',            current_settings["color-background"])
        document.documentElement.style.setProperty('--color-background-highlight',  current_settings["color-background-highlight"])
        document.documentElement.style.setProperty('--color-button',                current_settings["color-button"])
        document.documentElement.style.setProperty('--color-border',                current_settings["color-border"])
        document.documentElement.style.setProperty('--color-text',                  current_settings["color-text"])
        document.documentElement.style.setProperty('--color-dlbar-1',               current_settings["color-dlbar-1"] || current_settings["color-main"])
        document.documentElement.style.setProperty('--color-dlbar-2',               current_settings["color-dlbar-2"] || current_settings["color-main-highlight"])
    
        // --- Update config file
        this.webui_config_update();
    
    },
    webui_prompt_new_theme () {
        const root = document.documentElement;

        alert_box("New theme", `
            <p>The theme name can contain upper and lower case letters, numbers, underscores and hypens, must start with a letter and has to be unique.</p>
            <div class="settings-webui-new-theme">
                <div>Theme name:</div>
                <div><input type="text" class="s-webui-select-name" oninput="settings.webui_check_name(this)"></div>
                <div>Theme style:</div>
                <div>
                    <select class="s-webui-select-theme">
                        <option value="light"${getComputedStyle(root).getPropertyValue('--theme').trim() == "light" ? " selected" : ""}>Light mode</option>
                        <option value="dark"${getComputedStyle(root).getPropertyValue('--theme').trim() == "dark" ? " selected" : ""}>Dark mode</option>
                    </select>
                </div>
                <div>Main color:</div>
                <div><input type="text" class="color-input s-webui-select-color-main" value="${getComputedStyle(root).getPropertyValue('--color-main').trim()}" data-coloris oninput="document.querySelector('.s-webui-select-color-dlbar-1').value = this.value; document.querySelector('.s-webui-select-color-dlbar-1').dispatchEvent(new Event('input', { bubbles: true }));"></div>
                <div>Main highlight color:</div>
                <div><input type="text" class="color-input s-webui-select-color-main-highlight" value="${getComputedStyle(root).getPropertyValue('--color-main-highlight').trim()}" data-coloris oninput="document.querySelector('.s-webui-select-color-dlbar-1').value = this.value; document.querySelector('.s-webui-select-color-dlbar-1').dispatchEvent(new Event('input', { bubbles: true }));"></div>
                <div>Background color:</div>
                <div><input type="text" class="color-input s-webui-select-color-background" value="${getComputedStyle(root).getPropertyValue('--color-background').trim()}" data-coloris></div>
                <div>Background highlight color:</div>
                <div><input type="text" class="color-input s-webui-select-color-background-highlight" value="${getComputedStyle(root).getPropertyValue('--color-background-highlight').trim()}" data-coloris></div>
                <div>Button color:</div>
                <div><input type="text" class="color-input s-webui-select-color-button" value="${getComputedStyle(root).getPropertyValue('--color-button').trim()}" data-coloris></div>
                <div>Border color:</div>
                <div><input type="text" class="color-input s-webui-select-color-border" value="${getComputedStyle(root).getPropertyValue('--color-border').trim()}" data-coloris></div>
                <div>Text color:</div>
                <div><input type="text" class="color-input s-webui-select-color-text" value="${getComputedStyle(root).getPropertyValue('--color-text').trim()}" data-coloris></div>
                
                <div style="text-align: left" onclick="document.querySelectorAll('.color-input-extra').forEach(el => el.style.display = 'block')"><i>Click for advanced options</i></div><div></div>
                <div class="color-input-extra">Download bars use the main colors unless specified here</div><div class="color-input-extra"></div>
                <div class="color-input-extra">Download bar color 1:</div>
                <div><input type="text" class="color-input color-input-extra s-webui-select-color-dlbar-1" value="${getComputedStyle(root).getPropertyValue('--color-main').trim()}" data-coloris></div>
                <div class="color-input-extra">Download bar color 2:</div>
                <div><input type="text" class="color-input color-input-extra s-webui-select-color-dlbar-2" value="${getComputedStyle(root).getPropertyValue('--color-main-highlight').trim()}" data-coloris></div>

            </div>
            <br>
            <div class="popup-button-box">
                <button class="ui-button ui-button-small popup-exit disabled" id="webui-new-theme-ok" onclick="settings.webui_new_theme()" disabled>OK</button>
                <button class="ui-button ui-button-small popup-exit">Cancel</button>
            </div>  
        `);

        Coloris({ el: '.color-input' }); // --- update coloris
    },
    webui_check_name (target) {
        const regex = /^[A-Za-z][A-Za-z0-9 _-]*$/;
        const name = target.value.trim();

        if (regex.test(name) && !Object.hasOwn(this.webui_preset_themes, name) && !Object.hasOwn(this.webui_settings.custom_themes, name)) {
            document.getElementById("webui-new-theme-ok").classList.remove("disabled");
            document.getElementById("webui-new-theme-ok").disabled = false;
            document.getElementById("webui-new-theme-ok").title = "";

        } else {
            document.getElementById("webui-new-theme-ok").classList.add("disabled");
            document.getElementById("webui-new-theme-ok").disabled = true;
            document.getElementById("webui-new-theme-ok").title = "Theme name is invalid or is already in use.";
        }
    },
    webui_new_theme () {
        
        var new_item = {
            "theme": document.querySelector(".s-webui-select-theme").value,
            "color-main": document.querySelector(".s-webui-select-color-main").value,
            "color-main-highlight": document.querySelector(".s-webui-select-color-main-highlight").value,
            "color-background": document.querySelector(".s-webui-select-color-background").value,
            "color-background-highlight": document.querySelector(".s-webui-select-color-background-highlight").value,
            "color-button": document.querySelector(".s-webui-select-color-button").value,
            "color-border": document.querySelector(".s-webui-select-color-border").value,
            "color-text": document.querySelector(".s-webui-select-color-text").value,
            "color-dlbar-1": document.querySelector(".s-webui-select-color-dlbar-1").value,
            "color-dlbar-2": document.querySelector(".s-webui-select-color-dlbar-2").value,
        };

        // --- Add to UI
        var res = {};
        res[document.querySelector(".s-webui-select-name").value.trim()] = new_item;
        this.init_webui_appearance(res);

        // --- Add to JS
        this.webui_settings.custom_themes[document.querySelector(".s-webui-select-name").value] = new_item;

        // --- Update config file
        this.webui_config_update();
        
    },
    prompt_webui_delete_theme (theme_name) {
        alert_box("Attention!", `
            <p>Do you want to delete this theme?</p>
            <div class="popup-button-box">
                <button class="ui-button ui-button-small popup-exit"" onclick="settings.webui_delete_theme('${theme_name}')">OK</button>
                <button class="ui-button ui-button-small popup-exit">Cancel</button>
            </div>  
        `);
    },
    webui_delete_theme (theme_name) {
        console.log("--- Delete theme: " + theme_name);
        
        // --- Delete from UI
        var key = "s-webui-id-" + theme_name.replaceAll(" ", "-");
        document.getElementById(key).remove()

        // --- Delete from JS
        delete this.webui_settings.custom_themes[theme_name];

        // --- Delete from config file
        this.webui_config_update();

        // --- Set default theme again
        this.webui_update("SomeDL Dark");


    },
    prompt_webui_edit_theme (theme_name) {

        var values = this.webui_settings.custom_themes[theme_name]
    
        alert_box(`Edit theme "${theme_name}"`, `
            <div class="settings-webui-new-theme">
                <div>Theme style:</div>
                <div>
                    <select class="s-webui-select-theme">
                        <option value="light"${values['theme'] == "light" ? " selected" : ""}>Light mode</option>
                        <option value="dark"${values['theme'] == "dark" ? " selected" : ""}>Dark mode</option>
                    </select>
                </div>
                <div>Main color:</div>
                <div><input type="text" class="color-input s-webui-select-color-main" value="${values['color-main']}" data-coloris oninput="document.querySelector('.s-webui-select-color-dlbar-1').value = this.value; document.querySelector('.s-webui-select-color-dlbar-1').dispatchEvent(new Event('input', { bubbles: true }));"></div>
                <div>Main highlight color:</div>
                <div><input type="text" class="color-input s-webui-select-color-main-highlight" value="${values['color-main-highlight']}" data-coloris oninput="document.querySelector('.s-webui-select-color-dlbar-1').value = this.value; document.querySelector('.s-webui-select-color-dlbar-1').dispatchEvent(new Event('input', { bubbles: true }));"></div>
                <div>Background color:</div>
                <div><input type="text" class="color-input s-webui-select-color-background" value="${values['color-background']}" data-coloris></div>
                <div>Background highlight color:</div>
                <div><input type="text" class="color-input s-webui-select-color-background-highlight" value="${values['color-background-highlight']}" data-coloris></div>
                <div>Button color:</div>
                <div><input type="text" class="color-input s-webui-select-color-button" value="${values['color-button']}" data-coloris></div>
                <div>Border color:</div>
                <div><input type="text" class="color-input s-webui-select-color-border" value="${values['color-border']}" data-coloris></div>
                <div>Text color:</div>
                <div><input type="text" class="color-input s-webui-select-color-text" value="${values['color-text']}" data-coloris></div>

                <div style="text-align: left" onclick="document.querySelectorAll('.color-input-extra').forEach(el => el.style.display = 'block')"><i>Click for advanced options</i></div><div></div>
                <div class="color-input-extra">Download bars use the main colors unless specified here</div><div class="color-input-extra"></div>
                <div class="color-input-extra">Download bar color 1:</div>
                <div><input type="text" class="color-input color-input-extra s-webui-select-color-dlbar-1" value="${values['color-dlbar-1'] || values['color-main']}" data-coloris></div>
                <div class="color-input-extra">Download bar color 2:</div>
                <div><input type="text" class="color-input color-input-extra s-webui-select-color-dlbar-2" value="${values['color-dlbar-2'] || values['color-main-highlight']}" data-coloris></div>

            </div>
            <br>
            <div class="popup-button-box">
                <button class="ui-button ui-button-small popup-exit"" onclick="settings.webui_edit_theme('${theme_name}')">OK</button>
                <button class="ui-button ui-button-small popup-exit">Cancel</button>
            </div>  
        `);

        Coloris({ el: '.color-input' }); // --- update coloris

    },
    webui_edit_theme (theme_name) {
        var edited_item = {
            "theme": document.querySelector(".s-webui-select-theme").value,
            "color-main": document.querySelector(".s-webui-select-color-main").value,
            "color-main-highlight": document.querySelector(".s-webui-select-color-main-highlight").value,
            "color-background": document.querySelector(".s-webui-select-color-background").value,
            "color-background-highlight": document.querySelector(".s-webui-select-color-background-highlight").value,
            "color-button": document.querySelector(".s-webui-select-color-button").value,
            "color-border": document.querySelector(".s-webui-select-color-border").value,
            "color-text": document.querySelector(".s-webui-select-color-text").value,
            "color-dlbar-1": document.querySelector(".s-webui-select-color-dlbar-1").value,
            "color-dlbar-2": document.querySelector(".s-webui-select-color-dlbar-2").value,
        };

        // --- Add to UI
        var key = "s-webui-id-" + theme_name.replaceAll(" ", "-");
        var target = document.getElementById(key);

        target.querySelector(".s-webui-inp-color-main").style["background-color"] = edited_item["color-main"]
        target.querySelector(".s-webui-inp-color-main-highlight").style["background-color"] = edited_item["color-main-highlight"]
        target.querySelector(".s-webui-inp-color-background").style["background-color"] = edited_item["color-background"]
        target.querySelector(".s-webui-inp-color-background-highlight").style["background-color"] = edited_item["color-background-highlight"]
        target.querySelector(".s-webui-inp-color-button").style["background-color"] = edited_item["color-button"]
        target.querySelector(".s-webui-inp-color-border").style["background-color"] = edited_item["color-border"]
        target.querySelector(".s-webui-inp-color-text").style["color"] = edited_item["color-text"]

        // --- Add to JS
        this.webui_settings.custom_themes[theme_name] = edited_item;

        // --- Update webui
        this.webui_update(theme_name);

        // --- Update config file
        this.webui_config_update();

    },
    webui_config_update () {
        req_webui_config_save(this.webui_settings)
    },
    async webui_config_load () {
        var new_config = await req_webui_config_load();
        this.webui_settings = helper_deep_update(this.webui_settings, new_config);
    },



}

function helper_is_object(value) {
    return value && typeof value === "object" && !Array.isArray(value);
}

function helper_deep_update(target, source) {
    var result = { ...target };

    for (const key in source) {
        if (helper_is_object(source[key]) && helper_is_object(target[key])) {
            result[key] = helper_deep_update(target[key], source[key]);
        } else {
            result[key] = source[key];
        }
    }

    return result;
}


function alert_box(hdr, text) {
    var node = document.getElementById("alert-box");
    node.style.display = "flex";
    node.querySelector(".popup-hdr").innerHTML = hdr;
    node.querySelector(".popup-body").innerHTML = text;
    //     alert_box("hello", "world")
}

