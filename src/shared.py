import os


def add_name_arg(parser):
    parser.add_argument("-n", "--name", help="S3 Prefix Name")


def add_thread_arg(parser):
    parser.add_argument("thread_id", help="Thread ID of the conversation")


def add_prefix_arg(parser):
    parser.add_argument("prefix", type=str, help="S3 Prefix")


def add_collection_arg(parser):
    parser.add_argument("collection", type=str, help="Collection name")


def add_file_arg(parser):
    parser.add_argument("file", type=realpath_type, help="File location")


def realpath_type(value):
    return os.path.realpath(value)


def shorten_container_prefixes(c, prefix):
    items = c.get()
    items["ids"] = [i.replace(prefix, "", 1) if i.startswith(prefix) else i for i in items.get("ids")]
    for obj in items.get("metadatas"):
        if obj.get("source").startswith(prefix):
            obj["source"] = obj.get("source").replace(prefix, "", 1)
    return items


def add_bucket_arg(parser):
    parser.add_argument("-b", "--bucket", dest='bucket', type=str, help="S3 Bucket", default="perpetuator-user-uploads")


def add_all_arg(parser):
    parser.add_argument("-a", "--all", action="store_true", help="Print all items (else scoped to user context)")


def add_full_arg(parser):
    parser.add_argument("-f", "--full", action="store_true", help="Print full names")


def add_ids_arg(parser):
    parser.add_argument("-i", "--ids", nargs="+", help="IDs to delete")
