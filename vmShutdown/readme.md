Readme for VM State Monitor and Auto Shutdown

=============================================

This Python script is designed to monitor the state of virtual machines (VMs) in an Azure subscription and automatically shut down those that are tagged with a specific tag. It also sends a message to a Teams channel reporting the state of the VMs overnight.

Prerequisites

-------------

To use this script, you need:

-   An Azure subscription with VMs that need to be monitored and shut down.

-   Python 3.6 or later.

-   The Azure Python SDK (`azure-mgmt`).

-   A Teams webhook URL to send messages to the Teams channel.

Setup

-----

1\.  Install the Azure Python SDK (`azure-mgmt`) using pip:

    Copy code

    `pip install azure-mgmt`

2\.  Replace the sensitive data variables with your own values:

    -   `VMclientid`, `VMcsecretid`, and `VMtenantid`: Azure AD credentials for the VM resource management client.

    -   `Tagclientid`, `Tagcsecretid`, and `Tagtenantid`: Azure AD credentials for the subscription client.

    -   `vmWebhookUrl`: The Teams webhook URL to send messages to the Teams channel.

3\.  Set up the tag on the VMs that you want to shut down with the following key-value pair: `EnableShutdown: True`.

Usage

-----

The script will automatically run every day at two different times: 4:30 PM and 6:30 PM. It will check for VMs that have the `EnableShutdown: True` tag and shut them down if they are running. If no VMs are running, it will send a message to a Teams channel reporting that no VMs were on overnight.

Output

------

The script will output the following:

-   The current time.

-   A list of VMs that have the `EnableShutdown: True` tag.

-   The state of the VMs that were on overnight.

-   A message reporting the state of the VMs overnight to the Teams channel.

Conclusion

----------

This Python script provides an easy and automated way to monitor the state of VMs in an Azure subscription and shut down those that are tagged with a specific tag. It also sends a message to a Teams channel reporting the state of the VMs overnight. By using this script, you can save money on your Azure bill by shutting down VMs that are not needed outside of business hours.