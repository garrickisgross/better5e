mod home;
mod landing;
use home::Home;
use landing::Landing;
use iced::{widget::{button, column}, Element};

fn main() -> Result<(), iced::Error> {
    iced::run("better5e", Application::update, Application::view)
}

struct Application {
    //TODO: Convert this to a vector
    current_page: Box<dyn ViewTrait>
}

#[derive(Debug, Clone)]
enum Message {
    ChangePages(View),
}

#[derive(Debug, Clone)]
enum View {
    Home,
    Landing,
}

trait ViewTrait {
    fn update(&mut self, message: Message);
    fn view(&self) -> Element<'_, Message>;
}

impl Application {
    fn update(&mut self, message: Message) {
        match message {
            Message::ChangePages(view) => {
                match view {
                    View::Home => { self.current_page = Box::new(Home::new()) }
                    View::Landing => { self.current_page = Box::new(Landing::new())}
                }
            }



            // unreachable right now, but eventually we will be sending messages to pass to the page 
            _ => { self.current_page.update(message) }
        }
    }

    fn view(&self) -> Element<'_, Message> {
        let view = self.current_page.view();
        let home_button = button("Home").on_press(Message::ChangePages(View::Home));
        let landing_button = button("Landing").on_press(Message::ChangePages(View::Landing));
        let interface = column![view, landing_button, home_button];

        interface.into()
    }
}

impl Default for Application {
    fn default() -> Self {
        Application {current_page: Box::new(Landing::new())}
    }
}

