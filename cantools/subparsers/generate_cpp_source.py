import argparse
import importlib
import os
import os.path
import logging
import sys
import pathlib

from .. import database
from ..database.can.cpp_source import camel_to_snake_case, generate_message_class


def _do_generate_cpp_source(args):
    dbase = database.load_file(args.infile,
                               encoding=args.encoding,
                               prune_choices=args.prune,
                               strict=not args.no_strict)

    if args.database_name is None:
        basename = os.path.basename(args.infile)
        database_name = os.path.splitext(basename)[0]
        database_name = camel_to_snake_case(database_name)
    else:
        database_name = args.database_name

    for message in dbase.messages:
        file_name = database_name + '_' + camel_to_snake_case(message.name)
        filename_hpp = file_name + '.hpp'
        filename_cpp = file_name + '.cpp'
        # fuzzer_filename_c = file_name + '_fuzzer.c'
        # fuzzer_filename_mk = file_name + '_fuzzer.mk'

        # header, source, fuzzer_source, fuzzer_makefile = generate_message_class(
        header, source = generate_message_class(
            message,
            database_name,
            filename_hpp,
            filename_cpp,
            # fuzzer_filename_c,
            not args.no_floating_point_numbers,
            args.bit_fields,
            args.use_float,
            args.node)

        os.makedirs(args.output_directory, exist_ok=True)

        path_h = os.path.join(args.output_directory, filename_hpp)

        with open(path_h, 'w') as fout:
            fout.write(header)

        path_c = os.path.join(args.output_directory, filename_cpp)

        with open(path_c, 'w') as fout:
            fout.write(source)

        print(f'Successfully generated {path_h} and {path_c}.')

        # if args.generate_fuzzer:
        #     fuzzer_path_c = os.path.join(args.output_directory, fuzzer_filename_c)

        #     with open(fuzzer_path_c, 'w') as fout:
        #         fout.write(fuzzer_source)

        #     fuzzer_path_mk = os.path.join(args.output_directory, fuzzer_filename_mk)

        #     with open(fuzzer_filename_mk, 'w') as fout:
        #         fout.write(fuzzer_makefile)

        #     print('Successfully generated {} and {}.'.format(fuzzer_path_c,
        #                                                     fuzzer_path_mk))
        #     print()
        #     print(
        #         'Run "make -f {}" to build and run the fuzzer. Requires a'.format(
        #             fuzzer_filename_mk))
        #     print('recent version of clang.')


def add_subparser(subparsers):
    generate_cpp_source_parser = subparsers.add_parser(
        'generate_cpp_source',
        description='Generate C++ source code from given database file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    generate_cpp_source_parser.add_argument(
        '--database-name',
        help=('The database name.  Uses the stem of the input file name if not'
              ' specified.'))
    generate_cpp_source_parser.add_argument(
        '--no-floating-point-numbers',
        action='store_true',
        default=False,
        help='No floating point numbers in the generated code.')
    generate_cpp_source_parser.add_argument(
        '--bit-fields',
        action='store_true',
        help='Use bit fields to minimize struct sizes.')
    generate_cpp_source_parser.add_argument(
        '-e', '--encoding',
        help='File encoding.')
    generate_cpp_source_parser.add_argument(
        '--prune',
        action='store_true',
        help='Try to shorten the names of named signal choices.')
    generate_cpp_source_parser.add_argument(
        '--no-strict',
        action='store_true',
        help='Skip database consistency checks.')
    # generate_cpp_source_parser.add_argument(
    #     '-f', '--generate-fuzzer',
    #     action='store_true',
    #     help='Also generate fuzzer source code.')
    generate_cpp_source_parser.add_argument(
        '-o', '--output-directory',
        default='.',
        help='Directory in which to write output files.')
    generate_cpp_source_parser.add_argument(
        '--use-float',
        action='store_true',
        default=False,
        help='Use float instead of double for floating point generation.')
    generate_cpp_source_parser.add_argument(
        'infile',
        help='Input database file.')
    generate_cpp_source_parser.add_argument(
        '--node',
        help='Generate pack/unpack functions only for messages sent/received by the node.')
    generate_cpp_source_parser.set_defaults(func=_do_generate_cpp_source)
