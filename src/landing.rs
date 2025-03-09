use iced::widget::text;
use iced::Element;

use crate::ViewTrait;
use crate::Message;

pub struct Landing;


impl Landing {
    pub fn new() -> Self {
        Landing
    }
}

impl ViewTrait for Landing{
    
    fn update(&mut self, message: Message ) {
        match message {
            _ => {}
        }
    }

    fn view(&self) -> Element<'_, Message>{
        text("hello").into()
    }
}
