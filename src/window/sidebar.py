import os
import subprocess
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
from gettext import gettext as _
import textwrap

from window.preferences import show_preferences
from download.actionrow import on_download_clicked

def window_create_sidebar(self, variaapp, DownloadThread, variaVersion):
    sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    sidebar_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

    header_bar = Adw.HeaderBar()
    header_bar.get_style_context().add_class('flat')
    sidebar_box.append(header_bar)

    preferences_button = Gtk.Button(tooltip_text=_("Preferences"))
    preferences_button.set_icon_name("emblem-system-symbolic")
    preferences_button.connect("clicked", show_preferences, self, variaapp, variaVersion)

    hamburger_button = Gtk.MenuButton(tooltip_text=_("Other"))
    hamburger_button.set_icon_name("open-menu-symbolic")
    hamburger_menu_model = Gio.Menu()

    background_action = Gio.SimpleAction.new("background_mode", None)
    background_action.connect("activate", background_mode, self, variaapp)
    variaapp.add_action(background_action)

    cancel_all_action = Gio.SimpleAction.new("cancel_all_downloads", None)
    cancel_all_action.connect("activate", self.stop_all)
    variaapp.add_action(cancel_all_action)

    about_action = Gio.SimpleAction.new("downloads_folder", None)
    about_action.connect("activate", open_downloads_folder, self, self.appconf)
    variaapp.add_action(about_action)

    downloads_folder_action = Gio.SimpleAction.new("about", None)
    downloads_folder_action.connect("activate", show_about, self, variaVersion)
    variaapp.add_action(downloads_folder_action)

    self.shutdown_action = Gio.SimpleAction.new("shutdown_on_completion", None)
    self.shutdown_action.connect("activate", shutdown_on_completion, self)
    self.shutdown_action.set_enabled(False)
    variaapp.add_action(self.shutdown_action)

    self.exit_action = Gio.SimpleAction.new("exit_on_completion", None)
    self.exit_action.connect("activate", exit_on_completion, self)
    self.exit_action.set_enabled(False)
    variaapp.add_action(self.exit_action)

    hamburger_menu_item_background = Gio.MenuItem.new(_("Background Mode"), "app.background_mode")
    if (os.name != 'nt'):
        hamburger_menu_model.append_item(hamburger_menu_item_background)

    hamburger_menu_item_cancel_all = Gio.MenuItem.new(_("Cancel All"), "app.cancel_all_downloads")
    hamburger_menu_model.append_item(hamburger_menu_item_cancel_all)

    hamburger_menu_item_open_downloads_folder = Gio.MenuItem.new(_("Open Download Folder"), "app.downloads_folder")
    hamburger_menu_model.append_item(hamburger_menu_item_open_downloads_folder)

    completion_submenu_model = Gio.Menu()

    completion_submenu_item_exit = Gio.MenuItem.new(_("Exit on Completion"), "app.exit_on_completion")
    completion_submenu_model.append_item(completion_submenu_item_exit)

    completion_submenu_item_shutdown = Gio.MenuItem.new(_("Shutdown on Completion"), "app.shutdown_on_completion")
    completion_submenu_model.append_item(completion_submenu_item_shutdown)

    hamburger_menu_model.append_submenu(_("Completion Options"), completion_submenu_model)

    hamburger_menu_item_about = Gio.MenuItem.new(_("About Varia"), "app.about")
    hamburger_menu_model.append_item(hamburger_menu_item_about)

    hamburger_button.set_menu_model(hamburger_menu_model)

    header_bar.pack_start(preferences_button)
    header_bar.pack_end(hamburger_button)

    box_add_download = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    box_add_download.set_margin_start(8)
    box_add_download.set_margin_end(8)
    box_add_download.set_margin_top(8)
    box_add_download.set_margin_bottom(8)

    download_entry = Gtk.Entry()
    download_entry.set_placeholder_text(_("URL"))

    self.download_button_icon = Gtk.Image.new_from_icon_name("folder-download-symbolic")
    self.download_button_text = Gtk.Label(label=_("Download"))
    download_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    download_button_box.append(self.download_button_icon)
    download_button_box.append(self.download_button_text)

    self.download_button = Gtk.Button()
    self.download_button.set_child(download_button_box)
    self.download_button.get_style_context().add_class("suggested-action")
    self.download_button.set_sensitive(False)
    self.download_button.connect("clicked", on_download_clicked, self, download_entry, DownloadThread, None)

    self.video_button_icon = Gtk.Image.new_from_icon_name("emblem-videos-symbolic")
    self.video_button_text = Gtk.Label(label=_("Video Download"))
    video_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    video_button_box.append(self.video_button_icon)
    video_button_box.append(self.video_button_text)

    self.video_button = Gtk.Button()
    self.video_button.set_child(video_button_box)
    self.video_button.get_style_context().add_class("suggested-action")
    self.video_button.set_sensitive(False)
    self.video_button.connect("clicked", on_video_clicked, self, download_entry, DownloadThread, variaapp)

    download_entry.connect('changed', on_download_entry_changed, self.download_button, self.video_button)

    torrent_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    torrent_button_box.append(Gtk.Image.new_from_icon_name("document-open-symbolic"))
    torrent_button_box.append(Gtk.Label(label=_("Torrent")))

    add_torrent_button = Gtk.Button()
    add_torrent_button.get_style_context().add_class("suggested-action")
    add_torrent_button.set_child(torrent_button_box)
    add_torrent_button.connect("clicked", on_add_torrent_clicked, self)

    box_add_download.append(download_entry)
    box_add_download.append(self.download_button)
    box_add_download.append(self.video_button)
    box_add_download.append(Gtk.Separator(margin_top=8, margin_bottom=8))
    box_add_download.append(add_torrent_button)

    frame_add_download = Gtk.Frame()
    frame_add_download.set_margin_bottom(8)
    frame_add_download.set_child(box_add_download)

    self.filter_button_show_all = Gtk.ToggleButton()
    self.filter_button_show_all.get_style_context().add_class('flat')
    filter_button_show_all_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    filter_button_show_all_box.set_margin_top(8)
    filter_button_show_all_box.set_margin_bottom(8)
    filter_button_show_all_box.append(Gtk.Image.new_from_icon_name("switch-off-symbolic"))
    filter_button_show_all_label = Gtk.Label(label=_("All"))
    filter_button_show_all_label.get_style_context().add_class('body')
    filter_button_show_all_box.append(filter_button_show_all_label)
    self.filter_button_show_all.set_child(filter_button_show_all_box)
    self.filter_button_show_all.set_active(True)
    self.filter_button_show_all.connect("clicked", self.filter_download_list, "show_all")

    self.filter_button_show_downloading = Gtk.ToggleButton()
    self.filter_button_show_downloading.get_style_context().add_class('flat')
    filter_button_show_downloading_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    filter_button_show_downloading_box.set_margin_top(8)
    filter_button_show_downloading_box.set_margin_bottom(8)
    filter_button_show_downloading_box.append(Gtk.Image.new_from_icon_name("content-loading-symbolic"))
    filter_button_show_downloading_label = Gtk.Label(label=_("In Progress"))
    filter_button_show_downloading_label.get_style_context().add_class('body')
    filter_button_show_downloading_box.append(filter_button_show_downloading_label)
    self.filter_button_show_downloading.set_child(filter_button_show_downloading_box)
    self.filter_button_show_downloading.connect("clicked", self.filter_download_list, "show_downloading")

    self.filter_button_show_completed = Gtk.ToggleButton()
    self.filter_button_show_completed.get_style_context().add_class('flat')
    filter_button_show_completed_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    filter_button_show_completed_box.set_margin_top(8)
    filter_button_show_completed_box.set_margin_bottom(8)
    filter_button_show_completed_box.append(Gtk.Image.new_from_icon_name("emblem-ok-symbolic"))
    filter_button_show_completed_label = Gtk.Label(label=_("Completed"))
    filter_button_show_completed_label.get_style_context().add_class('body')
    filter_button_show_completed_box.append(filter_button_show_completed_label)
    self.filter_button_show_completed.set_child(filter_button_show_completed_box)
    self.filter_button_show_completed.connect("clicked", self.filter_download_list, "show_completed")

    self.filter_button_show_seeding = Gtk.ToggleButton()
    self.filter_button_show_seeding.get_style_context().add_class('flat')
    filter_button_show_seeding_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    filter_button_show_seeding_box.set_margin_top(8)
    filter_button_show_seeding_box.set_margin_bottom(8)
    filter_button_show_seeding_box.append(Gtk.Image.new_from_icon_name("go-up-symbolic"))
    filter_button_show_seeding_label = Gtk.Label(label=_("Seeding"))
    filter_button_show_seeding_label.get_style_context().add_class('body')
    filter_button_show_seeding_box.append(filter_button_show_seeding_label)
    self.filter_button_show_seeding.set_child(filter_button_show_seeding_box)
    self.filter_button_show_seeding.connect("clicked", self.filter_download_list, "show_seeding")

    self.filter_button_show_failed = Gtk.ToggleButton()
    self.filter_button_show_failed.get_style_context().add_class('flat')
    filter_button_show_failed_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    filter_button_show_failed_box.set_margin_top(8)
    filter_button_show_failed_box.set_margin_bottom(8)
    filter_button_show_failed_box.append(Gtk.Image.new_from_icon_name("process-stop-symbolic"))
    filter_button_show_failed_label = Gtk.Label(label=_("Failed"))
    filter_button_show_failed_label.get_style_context().add_class('body')
    filter_button_show_failed_box.append(filter_button_show_failed_label)
    self.filter_button_show_failed.set_child(filter_button_show_failed_box)
    self.filter_button_show_failed.connect("clicked", self.filter_download_list, "show_failed")

    self.sidebar_shutdown_mode_label = Gtk.Label()
    self.sidebar_remote_mode_label = Gtk.Label()
    if (self.appconf['remote'] == '1'):
        self.sidebar_remote_mode_label.set_text(textwrap.fill(_("Remote Mode"), 23))
    self.sidebar_speed_limited_label = Gtk.Label()
    self.sidebar_scheduler_label = Gtk.Label()

    sidebar_content_box.set_margin_start(6)
    sidebar_content_box.set_margin_end(6)
    sidebar_content_box.set_margin_bottom(6)

    sidebar_filter_buttons_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    sidebar_filter_buttons_box.append(self.filter_button_show_all)
    sidebar_filter_buttons_box.append(self.filter_button_show_downloading)
    sidebar_filter_buttons_box.append(self.filter_button_show_completed)
    sidebar_filter_buttons_box.append(self.filter_button_show_seeding)
    sidebar_filter_buttons_box.append(self.filter_button_show_failed)

    sidebar_content_box.append(frame_add_download)
    sidebar_content_box.append(sidebar_filter_buttons_box)
    sidebar_content_box.append(Gtk.Box(vexpand=True))
    sidebar_content_box.append(self.sidebar_shutdown_mode_label)
    sidebar_content_box.append(self.sidebar_remote_mode_label)
    sidebar_content_box.append(self.sidebar_speed_limited_label)
    sidebar_content_box.append(self.sidebar_scheduler_label)
    sidebar_box.append(sidebar_content_box)

    self.overlay_split_view.set_sidebar(sidebar_box)

def on_download_entry_changed(entry, download_button, video_button):
    if entry.get_text() != "":
        download_button.set_sensitive(True)
        video_button.set_sensitive(True)
    else:
        download_button.set_sensitive(False)
        video_button.set_sensitive(False)

def on_video_clicked(button, self, entry, DownloadThread, variaapp):
    url = entry.get_text()
    entry.set_text("")

    # Show loading screen
    loading_dialog = Adw.AlertDialog()
    loading_dialog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=25)
    loading_dialog.set_child(loading_dialog_box)
    loading_dialog_box.set_margin_top(30)
    loading_dialog_box.set_margin_bottom(30)
    loading_dialog_box.set_margin_start(60)
    loading_dialog_box.set_margin_end(60)
    loading_dialog_spinner = Adw.Spinner()
    loading_dialog_spinner.set_size_request(30, 30)
    loading_dialog_box.append(loading_dialog_spinner)
    loading_dialog_label = Gtk.Label(label=_("Checking video..."))
    loading_dialog_label.get_style_context().add_class("title-1")
    loading_dialog_box.append(loading_dialog_label)
    loading_dialog.set_can_close(False)
    loading_dialog.present(self)

    def ytdlp_startsubprocess():
        ytdlp_subprocess = subprocess.Popen(["yt-dlp", "--print", "title", "-F", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ytdlp_subprocess.wait()

        quality_options = []
        video_title = ""
        while True:
            process_return_code = ytdlp_subprocess.poll()
            if process_return_code is not None:
                stdout, stderr = ytdlp_subprocess.communicate()
                if process_return_code == 0:
                    i = 0
                    options_list_length = len(stdout.split('\n'))

                    for line in stdout.split('\n'):

                        if i == options_list_length - 2:
                            video_title = line

                        elif line.strip() and line[0].isdigit():
                            line = line.split(" ")
                            
                            while "" in line:
                                line.remove("")

                            new_quality_option = []
                            new_quality_option.append(line[0])
                            new_quality_option.append(line[1])
                            new_quality_option.append(line[2])

                            if line[2] == "audio":
                                new_quality_option.append("audio")
                            else:
                                new_quality_option.append(line[3])
                            
                            video_filesize = ""

                            if line[line.index("|") + 1].startswith("~") or line[line.index("|") + 1].startswith("≈"):
                                video_filesize = line[line.index("|") + 1]
                                if len(line[line.index("|") + 1]) == 1:
                                    video_filesize += line[line.index("|") + 2]

                            elif line[line.index("|") + 1][0].isnumeric():
                                video_filesize = line[line.index("|") + 1]
                            
                            new_quality_option.append(video_filesize)
                            
                            quality_options.append(new_quality_option)
                        
                        i += 1

                break
        
        GLib.idle_add(loading_dialog.set_can_close, True)
        GLib.idle_add(loading_dialog.close)

        if len(quality_options) > 0:
            # Show video download options
            video_download_options_preferences_dialog = Adw.PreferencesDialog(title=_("Download Video"))
            page = Adw.PreferencesPage()
            video_download_options_preferences_dialog.add(page)
            print(video_title)
            group = Adw.PreferencesGroup(title="\"" + video_title + "\"")
            page.add(group)

            i = 0
            for video_option in quality_options:
                video_option_actionrow = Adw.ActionRow()

                if video_option[2] == "audio":
                    if video_option[4] == "":
                        video_option_actionrow.set_title(_("Audio only"))
                    else:
                        video_option_actionrow.set_title(_("Audio only") + "  ·  " + video_option[4])

                    video_option_actionrow.set_subtitle(video_option[1])
                else:
                    if video_option[4] == "":
                        video_option_actionrow.set_title(_("Video"))
                    else:
                        video_option_actionrow.set_title(_("Video") + "  ·  " + video_option[4])

                    if video_option[3] == "audio":
                        video_option_actionrow.set_subtitle(video_option[1] + "  ·  " + video_option[2])
                    else:
                        video_option_actionrow.set_subtitle(video_option[1] + "  ·  " + video_option[2] + "  ·  " + video_option[3] + "fps")
                
                video_download_button = Gtk.Button(label=_("Download"))
                video_download_button.get_style_context().add_class("suggested-action")
                video_download_button.set_halign(Gtk.Align.START)
                video_download_button.set_valign(Gtk.Align.CENTER)
                video_download_button.connect("clicked", lambda clicked, video_format=video_option[0], download_name=video_title, download_extension=video_option[1]: on_video_option_download_clicked(self, video_download_options_preferences_dialog, video_option_actionrow, video_format, download_name, download_extension, url, DownloadThread))
                video_option_actionrow.add_suffix(video_download_button)

                group.add(video_option_actionrow)
                i += 1
            
            GLib.idle_add(video_download_options_preferences_dialog.present, self)

        return
    
    thread = threading.Thread(target=lambda: ytdlp_startsubprocess())
    thread.start()

def on_video_option_download_clicked(self, prefswindow, actionrow, video_format, download_name, download_extension, url, DownloadThread):
    prefswindow.close()
    print(url)
    print(video_format)

    loading_dialog = Adw.AlertDialog()
    loading_dialog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=25)
    loading_dialog.set_child(loading_dialog_box)
    loading_dialog_box.set_margin_top(30)
    loading_dialog_box.set_margin_bottom(30)
    loading_dialog_box.set_margin_start(60)
    loading_dialog_box.set_margin_end(60)
    loading_dialog_spinner = Adw.Spinner()
    loading_dialog_spinner.set_size_request(30, 30)
    loading_dialog_box.append(loading_dialog_spinner)
    loading_dialog_label = Gtk.Label(label=_("Starting download..."))
    loading_dialog_label.get_style_context().add_class("title-1")
    loading_dialog_box.append(loading_dialog_label)
    loading_dialog.set_can_close(False)
    loading_dialog.present(self)

    def ytdlp_startsubprocess():
        ytdlp_subprocess = subprocess.Popen(["yt-dlp", "-f", video_format, "-g", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ytdlp_subprocess.wait()

        video_download_link = ""
        while True:
            process_return_code = ytdlp_subprocess.poll()
            if process_return_code is not None:
                stdout, stderr = ytdlp_subprocess.communicate()
                if process_return_code == 0:
                    video_download_link = stdout
                break
                
        if video_download_link != "":
            on_download_clicked(None, self, video_download_link, DownloadThread, download_name + "." + download_extension)
        
        GLib.idle_add(loading_dialog.set_can_close, True)
        GLib.idle_add(loading_dialog.close)
        
        return

    thread = threading.Thread(target=lambda: ytdlp_startsubprocess())
    thread.start()

def on_add_torrent_clicked(self, variaapp):
    file_filter = Gtk.FileFilter()
    file_filter.add_pattern("*.torrent")
    dialog = Gtk.FileDialog(default_filter=file_filter)
    dialog.open(variaapp, None, on_add_torrent, variaapp)

def on_add_torrent(file_dialog, result, self):
    try:
        file = file_dialog.open_finish(result).get_path()
    except:
        return
    if file.endswith(".torrent"):
        self.api.add_torrent(file)

def background_mode(app, variaapp1, self, variaapp):
    self.exitProgram(app=app, variaapp=variaapp, background=True)

def show_about(app, variaapp, self, variaVersion):
    dialog = Adw.AboutDialog()
    dialog.set_application_name("Varia")
    dialog.set_version(variaVersion)
    dialog.set_developer_name("Giant Pink Robots!")
    dialog.set_license_type(Gtk.License(Gtk.License.MPL_2_0))
    dialog.set_comments(_("aria2 based download manager utilizing GTK4 and Libadwaita."))
    dialog.set_website("https://giantpinkrobots.github.io/varia")
    dialog.set_issue_url("https://github.com/giantpinkrobots/varia/issues")
    dialog.set_copyright("2023 Giant Pink Robots!\n\n" + _("This application relies on the following pieces of software:") +
        "\n\n- aria2\n- GTK4\n- Libadwaita\n- Meson\n- OpenSSL\n- Python-appdirs\n- Python-aria2p\n- Python-certifi\n- Python-charset-normalizer\n- Python-gettext\n- Python-idna\n- Python-loguru\n- Python-requests\n- Python-setuptools\n- Python-urllib3\n- Python-websocket-client\n\n" +
        _("The licenses of all of these pieces of software can be found in the dependencies_information directory in this application's app directory."))
    dialog.set_developers(["Giant Pink Robots! (@giantpinkrobots) https://github.com/giantpinkrobots"])
    dialog.set_application_icon("io.github.giantpinkrobots.varia")
    dialog.set_translator_credits(_("translator-credits"))
    dialog.set_artists(["Jakub Steiner"])
    dialog.set_release_notes_version("v2024.11.7")
    dialog.set_release_notes('''
        <ul><li>Support for opening .torrent files.</li>
        <li>Downloads now show the estimated time remaining.</li>
        <li>UI tweaks and fixes for a better layout.</li>
        <li>Remote mode option is available again.</li>
        <li>A lot of under the hood changes to fix bugs and improve performance.</li>
        <li>Update to the GNOME 47 runtime and new Libadwaita widgets.</li>
        <li>Support for Bulgarian and Chinese (China) languages.</li>
        <li>(Only on Windows) Automatic update function.</li>
        <li>(Only on Windows) Support for localization.</li>
        <li>(Only on Windows) All icons are shown properly everywhere.</li></ul>''')

    dialog.present(self)

def open_downloads_folder(self, app, variaapp, appconf):
    if (os.name == 'nt'):
        os.startfile(appconf["download_directory"])
    else:
        subprocess.Popen(["xdg-open", appconf["download_directory"]])

def shutdown_on_completion(self, app, variaapp):
    if (variaapp.shutdown_mode == False):
        variaapp.shutdown_mode = True
        variaapp.exit_mode = False
        variaapp.sidebar_remote_mode_label.set_text(textwrap.fill(_("Shutdown on Completion"), 23))
    else:
        variaapp.shutdown_mode = False
        variaapp.sidebar_remote_mode_label.set_text("")

def exit_on_completion(self, app, variaapp):
    if (variaapp.exit_mode == False):
        variaapp.exit_mode = True
        variaapp.shutdown_mode = False
        variaapp.sidebar_remote_mode_label.set_text(textwrap.fill(_("Exit on Completion"), 23))
    else:
        variaapp.exit_mode = False
        variaapp.sidebar_remote_mode_label.set_text("")
