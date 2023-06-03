import pynecone as pc
base_style = {
    pc.Heading: {
        "font_size":"2em", 
        "background_image":"linear-gradient(271.68deg, #211344 25%, #443213 50% )",
        "background_clip":"text",
    },
    pc.Button: {
        "border": "0.15em solid",
        "border_radius": "0.5em",
        "padding": "0.5em",
        "_hover": {
            "color": "rgb(107,99,246)",
        },
    },
    pc.Link:{
        "href":"#",
        "border":"0.1em solid",
        "padding":"0.1em",
        "border_radius":"0.5em",
        "_hover":{
            "color": "rgb(107,99,246)",
        },
        "font_size":["2em", "3em", "3em", "4em"],
        "font_weight":800,
        "font_family":"Inter",
        "background_image":"linear-gradient(271.68deg, #EE756A 25%, #756AEE 50%)",
        "background_clip":"text",
    }
}
