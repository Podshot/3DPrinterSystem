import os

base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_directory = os.path.join(
                              base_directory,
                              "data"
                              )

upload_directory = os.path.join(
                                base_directory,
                                "uploads"
                                )

template_directory = os.path.join(
                                  base_directory,
                                  "templates"
                                  )

static_directory = os.path.join(
                                base_directory,
                                "static"
                                )
