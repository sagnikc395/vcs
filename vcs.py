import sys 
import argparse



def main(argv=sys.argv[1:]): # type: ignore
    argparser = argparse.ArgumentParser(description="a mini git like vcs")
    argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
    argsubparsers.required = True 
    
    args = argparser.parse_args(argv) # type: ignore
    match args.command:
        case "add": cmd_add(args)
        case "cat-file": cmd_cat_file(args)
        case "check-ignore": cmd_check_ignore(args)
        case "checkout":   cmd_checkout(args)
        case "commit": cmd_commit(args)
        case "hash-object": cmd_hash_object(args)
        case "init": cmd_init(args)
        case "log": cmd_log(args)
        case "ls-files": cmd_ls_files(args)
        case "ls-tree": cmd_ls_tree(args)
        case "rev-parse": cmd_rev_parse(args)
        case "rm": cmd_rm(args)
        case "show-ref": cmd_show_red(args)
        case "status": cmd_status(args)
        case "tag": cmd_tag(args)
        case _ : print("Bad command.")
        
        