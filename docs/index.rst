.. Exonum Python light client documentation master file, created by
   sphinx-quickstart on Tue Sep 17 12:22:21 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Exonum Python light client's documentation!
======================================================

========
Overview
========

Exonum light client is a Python library for working with Exonum blockchain
from the client side. It can be easily integrated to an existing
application. Also, Exonum light client provides access to common utils
toolkit which contains some helpful functions for hashing, cryptography,
serialization, etc.

============
Capabilities
============

By using the client you are able to perform the following operations:

- Submit transactions to the node
- Receive information on transactions
- Receive information on blockchain blocks
- Receive information on the node system
- Receive information on the node status

===================
System Dependencies
===================

- Python 3.5 or above.
- Package installer for Python3 (pip3)

========
Examples
========

The following example shows how to create an instance of the Exonum client
which will be able to work with Exonum node with
cryptocurrency-advanced service, at http://localhost:8080
address:

------------------------------
Installing Python Light Client
------------------------------

First of all we need to install our client library:

::

    git clone git@github.com:exonum/python-client.git
    pip3 install -e python-client

----------------------------
Exonum Client Initialization
----------------------------

>>> from exonum import ExonumClient, MessageGenerator, ModuleManager, gen_keypair
>>> client = ExonumClient(hostname="localhost", public_api_port=8080, private_api_port=8081, ssl=False)


---------------------
Compiling Proto Files
---------------------

To compile proto files into the Python analogues we need a protobuf loader.

>>> with client.protobuf_loader() as loader:
>>>     #  Your code goes here.

Since loader acquires resources on initialization, creating via context manager is recommended.
Otherwise you should initialize and deinitialize client manually:

>>> loader = client.protobuf_loader()
>>> loader.initialize()
>>> # ... Some usage
>>> loader.deinitialize()

Then we need to run the following code:

>>> loader.load_main_proto_files()  # Load and compile main proto files, such as `runtime.proto`, `consensus.proto`, etc.
>>> loader.load_service_proto_files(runtime_id=0, service_name='exonum-supervisor:0.12.0')  # Same for specific service.

- runtime_id=0 here means, that service works in Rust runtime.

-----------------------------
Creating Transaction Messages
-----------------------------

The following example shows how to create a transaction message.

>>> from exonum.crypto import KeyPair
>>> keys = KeyPair.generate()
>>> cryptocurrency_service_name = 'exonum-cryptocurrency-advanced:0.11.0'
>>> loader.load_service_proto_files(runtime_id=0, cryptocurrency_service_name)
>>> cryptocurrency_module = ModuleManager.import_service_module(cryptocurrency_service_name, 'service')
>>> cryptocurrency_message_generator = MessageGenerator(service_id=1024, service_name=cryptocurrency_service_name)
>>> create_wallet_alice = cryptocurrency_module.CreateWallet()
>>> create_wallet_alice.name = 'Alice'
>>> create_wallet_alice_tx = cryptocurrency_message_generator.create_message('CreateWallet', create_wallet_alice)
>>> create_wallet_alice_tx.sign(keys)

- 1024 - service instance ID.
- "CreateWallet" - name of the message.
- key_pair - public and private keys of the ed25519 public-key signature system.

After invoking sign method we get a signed transaction. 
This transaction is ready for sending to the Exonum node.

-----------------------------------
Getting data on availiable services
-----------------------------------

Code below will show list of artifacts available to start, and list of working services.

>>> client.available_services().json()
{
  'artifacts': [
    {
      'runtime_id': 0,
      'name': 'exonum-cryptocurrency-advanced:0.11.0'
    },
    {
      'runtime_id': 0,
      'name': 'exonum-supervisor:0.11.0'
    }
  ],
  'services': [
    {
      'id': 1024,
      'name': 'XNM',
      'artifact': {
        'runtime_id': 0,
        'name': 'exonum-cryptocurrency-advanced:0.11.0'
      }
    },
    {
      'id': 0,
      'name': 'supervisor',
      'artifact': {
        'runtime_id': 0,
        'name': 'exonum-supervisor:0.11.0'
      }
    }
  ]
}

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`