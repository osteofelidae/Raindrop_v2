# FILE: Set default files


# DEPENDENCIES
import io_2


# MAIN
if __name__ == "__main__":

    # Config defaults
    config = {
        "configured": "True",  # Whether config is configured correctly
        "colors": {  # Colors
            "generic": 0x00FFFF,  # General embeds
            "error": 0xFF9494,  # Error embeds
            "success": 0x94FF94  # Success embeds
        }
    }

    # Data defaults
    data = {
        "configured": "True",  # Whether data is configured correctly
        "streams": {
            "<example_stream_id>": {
                "locked": "True",  # Whether stream is accessible/mutable
                "origin_server": "<example_server_id>",  # Server where stream was created
                "whitelist": [  # Objects that can edit this stream
                    "<example_snowflake_id_1>",
                    "<example_snowflake_id_2>",
                    "<example_snowflake_id_3>"
                ],
                "blacklist": [  # Objects that cannot edit this stream
                    "<example_snowflake_id_1>",
                    "<example_snowflake_id_2>",
                    "<example_snowflake_id_3>"
                ],
                "channels": [  # Channels to write to when announcement posted to stream
                    "<example_channel_id_1>",
                    "<example_channel_id_2>",
                    "<example_channel_id_3>"
                ]
            }
        },
        "whitelist": [  # Whitelisted ids
            "<example_snowflake_id_1>",
            "<example_snowflake_id_2>",
            "<example_snowflake_id_3>"
        ],
        "blacklist": [  # Blacklisted ids
            "<example_snowflake_id_1>",
            "<example_snowflake_id_2>",
            "<example_snowflake_id_3>"
        ],
        "admins": [  # Bot administrator ids
            "446592818136219648"  # reshaye
        ]
    }

    # Write files
    io_2.write_json(file_path="config_defaults.json",
                    data=config)
    io_2.write_json(file_path="data_defaults.json",
                    data=data)