use iced::widget::text;
use iced::Element;

use crate::ViewTrait;
use crate::Message;

pub struct Home;


impl Home {
    pub fn new() -> Self {
        Home
    }
}

impl ViewTrait for Home{
    
    fn update(&mut self, message: Message ) {
        match message {
            _ => {}
        }
    }

    fn view(&self) -> Element<'_, Message>{
        text("world").into()
    }
}
