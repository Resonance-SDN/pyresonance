import subprocess
import platform
import os

class ModelChecker(object):
    
    def __init__(self, policy):
        filename = policy.name()
        fsm_desc = policy.fsm_description 
        arch_str = platform.architecture()
        if arch_str:
            if not os.environ.has_key('PYRESOPATH'):
                print 'PYRESOPATH env variable not set. Set it with export command.'
                return
            pyreso_path_str = os.environ['PYRESOPATH']
            if arch_str[0].startswith('32'):  
                self.exec_cmd = pyreso_path_str + '/smv/NuSMV_32'
            else:
                self.exec_cmd = pyreso_path_str + '/smv/NuSMV_64'
        self.smv_file_directory = pyreso_path_str + '/smv/smv_files/'

        # Translate and create smv file
#        path_to_file = self.translate_to_smv_file(fsm_desc, filename)

        path_to_file = os.path.join(self.smv_file_directory,filename+'.smv')

        # Feed into nusmv
        self.feed_to_nusmv(path_to_file)

    def translate_to_smv_file(self, fsm_desc, filename):
        ### Start out
        smv_str = "MODULE main\n"
        
        ## VAR and INIT ##
        var_init_str = self.var_and_init(fsm_desc)

        # Transition
        transition_str =  self.get_transition_relation(fsm_desc)

        ### SPEC ###
        spec_str = "\n"
#        spec_str = "SPEC\n"

        ### Add up, write, close.
        smv_str = smv_str + var_init_str + transition_str + spec_str
        fd = open(self.smv_file_directory + filename + '.smv', 'w')
        fd.write(smv_str)
        path_to_file = fd.name
        fd.close()

        return path_to_file


    def var_and_init(self, fsm_desc):
         ### VAR section ###
        var_str = "VAR\n"
        state_init_dict = {}
        for var, props in fsm_desc.items():
            state_type, init_value, next_fn = props

            # Type boolean
            if state_type == bool:
                var_str = var_str + '  ' + str(var) + ' : boolean;\n'

            # Type list
            elif type(state_type) == list:
                var_str = var_str + '  ' + str(var) + ' : {'
                for state in state_type:
                    var_str = var_str + str(state) + ','
                var_str = var_str.rstrip(',') + '};\n'

            else:
                print 'Else type.'
                print type(state_type)
  
            # Store init value
            state_init_dict[str(var)] = str(init_value)

        ### ASSIGN section ###
        assign_str = "ASSIGN\n"
        # Init
        for s in state_init_dict:
            if state_init_dict[s] == 'True' or state_init_dict[s] == 'False':
                state_init_value = state_init_dict[s].upper()
            else:
                state_init_value = state_init_dict[s]
            assign_str = assign_str + ' init(' + s + ') := ' + state_init_value + ';\n'

        return var_str + assign_str


    # def get_transition_relation(self, fsm_desc):

    #     def foo(fn):
    #         if not fn:
    #             return

    #         print '-------------'
    #         print fn
    #         for test,ret in fn.cases:
    #             print 'test'
    #             print test
    #             print 'ret'
    #             print ret
            
    #         # fn_src = inspect.getsource(fn)
    #         # fn_src = textwrap.dedent(fn_src)
    #         # print fn_src
    #         # fn_ast = ast.parse(fn_src)
    #         # print fn_ast
    #         # print ast.dump(fn_ast)

    #     for var, props in fsm_desc.items():
    #         state_type, init_value, next_fn = props

    #         foo(next_fn.event_fn)
    #         foo(next_fn.state_fn)

    #     return transiton_str


    def feed_to_nusmv(self, path_to_file):
       
        print '========================== NuSMV OUTPUT ==========================\n'

        p = subprocess.Popen([self.exec_cmd, '-r', path_to_file], stdout=subprocess.PIPE) 
        out, err = p.communicate()

        print out

        print '======================== NuSMV OUTPUT END ========================\n'
