function onIPyHook() {
    var browserWindow = window.parent.parent,
        token = browserWindow.IPY_VARS.OAUTH_TOKEN,
        auth = token ? {token: token} : undefined;

    console.log('token is', token);
    window.OAUTH_TOKEN = token;

    console.log('onIPyHook: token=' + browserWindow.IPY_VARS.OAUTH_TOKEN)

    // Create the editor...
    var editor = new MDSEditor({
        openProjectBtn: document.getElementById('open-project'),
        loginBtn: document.getElementById('login'),
        logoutBtn: document.getElementById('logout'),
        auth: auth
    });

    // Download, Save buttons
    document.getElementById('download').onclick = editor.downloadActiveWorkspace.bind(editor);
    document.getElementById('save').onclick = editor.saveProject.bind(editor);
    document.getElementById('toggle-editor').onclick = editor.toggleCodeEditor.bind(editor);

    var repo = browserWindow.IPY_VARS.DEFAULT_PROJECT;
    if(repo) {
        if(window.DEFAULT_PROJECT != repo) {
            window.DEFAULT_PROJECT = repo;
            editor.loadProject(repo);
        }
    }

    var IPython = browserWindow.IPython;

    // hook on 'save' action
    var oldOnClick = document.getElementById('save').onclick;
    document.getElementById('save').onclick = function(e) {
        oldOnClick();

        // create a command that
        // 1. gets the editor_id to editor mapping from the module scope
        // 2. makes editor_<editor_id> assigned to the python editor object
        // 3. sets 'finished' property to true
        // 4. removes the module and editor from the namespace [TODO]
        var command = "import simgen.mdsblocks.editor as smds_ed;" +
            "editor_" + browserWindow.IPY_VARS.EDITOR_ID + " = smds_ed.id_to_editor_map[" + browserWindow.IPY_VARS.EDITOR_ID + "];" +
            "editor_" + browserWindow.IPY_VARS.EDITOR_ID + ".finished = True";
        console.log("Executing command " + command);
        var kernel = IPython.notebook.kernel;
        kernel.execute(command);
    }
}
