### v0.18
##### 11/02/2021
- add ability to handle ChatWriteForbiddenError exception
  - instead of failing completely for the channel, will instead sleep for 1 hour

### v0.17
##### 10/29/2021
- bug fix to ensure random thank yous are indeed random

### v0.16
##### 10/29/2021
- just adding some color to the output

### v0.15
##### 10/28/2021
- added ability to define the maximum number of messages sent to a channel
  - option is `total_messages`
  - this allows a user to NOT SPAM a channel once they feel they have sent enough messages
  - might help build/maintain their rep
  - example:
  ```yaml
  channel_with_max_total:
    message_type: some_message
    wait_interval: 600
    total_messages: 100
  ...
  ```
- added a banner to the startup, maybe it will discourage wankers ?? doubt it

### v0.14
##### 10/20/2021
- added ability to define multiple message types per channel
  - only one message will be sent per wait interval
  - messages will be sent in the user defined order, so for the below YAML example, the order is:
    - `some_message`, wait interval;
    - `some_other_message`, wait interval;
    - `some_awesome_message`, wait interval;
    - repeat
  - example:
  ```yaml
  channel_with_many_message_types:
    message_type:
    - some_message
    - some_other_message
    - some_awesome_message
    wait_interval: 600
  channel_with_one_message_type:
    message_type: some_message
    wait_interval: 600
  ...
  ```
- broked out some code to be more pure
- added more schema validation to ensure `wait_interval` and `increase_wait_interval` are greater than 0, when defined
- added more unit tests

### v0.13
##### 10/19/2021
- added `phone_number` as a required config option, thus cutting down on having to type it in during startup
  - example:
  ```yaml
  ---

  api_id: 123456
  api_hash: abc123456YXZ
  app_short_name: SomeAppName
  phone_number: "+18888675309"
  ...
  ```
- added many more `settings.yml` validation tests, so startup will fail early if not config'ed properly
  - related to account settings, message settings, and raid settings
- added new possible exception error related to "message too long"
- added more verbose output when an unknown exception occurs
- only recalc wait interval if message is in a loop

### v0.12
##### 10/12/2021
- try and improve Telethon flood wait error handling

### v0.11
##### 10/7/2021
- mostly a developer upgrade
  - added start of unit testing
  - added new `Makefile` commands
  - added 1st go at YAML validation, both at the file load level and the actual data level
    - using `jsonschema` here
  - refactored use of GLOBAL vars and cut down on those alot
  - rolled `open file` bare method into function
  - functionized some complicated `getting` on some next Dicts
  - added FAIL message if simple YAML file can't even be loaded

### v0.10
##### 10/5/2021
- added `image` as a config option (not required), allowing users to send an image with their messages
  - example:
  ```yaml
  ...
  # this example will send the "short" message and relative image "images/my-awhsum.jpg"
  # once every 10 minutues (600 seconds)
  somerandomchannelname:
    message_type: short
    wait_interval: 600
    image: images/my-awhsum.jpg
  ...
  ```

### v0.9
##### 10/4/2021
- added `increase_wait_interval` as a config option, allowing users to gradually increase how frequent messages are sent to a channel
  - example:
  ```yaml
  ...
  # this example will send a message once every 10 minutues (600 seconds)
  # after every iteration, 1 minute (60 seconds) will be added to the previous attempt's wait interval
  # so here is an example sequence of operations:
  #   - 10m wait, send message, 10m + 1m = 11m
  #   - 11m wait, send message, 11m + 1m = 12m
  #   - 12m wait, send message, 12m + 1m = 13m
  #   - etc, etc, etc
  somerandomchannelname:
    message_type: short
    wait_interval: 600
    increase_wait_interval: 60
  ...
  ```

### v0.8
##### 10/1/2021
- improved Telethon error handling

### v0.7
##### 9/30/2021
- refactored `channel` implementation

### v0.6
##### 9/28/2021
- refactored `splay` implementation

### v0.5
##### 9/27/2021
- added `splay` to connection and message calls to avoid `FloodWaitError` errors

### v0.4
##### 9/24/2021
- added Telethon entity caching to avoid `FloodWaitError` errors

### v0.3
##### 9/23/2021
- added random `thank you`s to end of message to avoid getting banned

### v0.2
##### 9/9/2021
- added try/catch around `FloodWaitError` errors

### v0.1
- Hello, World!
