import os


data_directory = os.path.join(
                              os.path.dirname(
                                              os.path.abspath(
                                                              __file__
                                                              )
                                              ),
                              "data")

upload_directory = os.path.join(
                                os.path.dirname(
                                                os.path.abspath(
                                                                __file__
                                                                )
                                                ), 
                                "uploads")

template_directory = os.path.join(
                                  os.path.dirname(
                                                  os.path.abspath(
                                                                  __file__
                                                                  )
                                                  ),
                                  "templates")
