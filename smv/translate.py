################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Joshua Reich (jreich@cs.princeton.edu)                               #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################


import subprocess
import platform

class ModelChecker(object):
    
    def __init__(self, fsm_desc, filename):
        arch_str = platform.architecture()
        if arch_str:
            if arch_str[0].startswith('32'):  
                self.exec_cmd = './smv/NuSMV_32'
            else:
                self.exec_cmd = './smv/NuSMV_64'
        self.smv_file_directory = './smv/smv_files/'

        # Translate and create smv file
        path_to_file = self.translate_to_smv_file(fsm_desc, filename)

        # Feed into nusmv
        self.feed_to_nusmv(path_to_file)

    def translate_to_smv_file(self, fsm_desc, filename):
        ### Start out
        smv_str = "MODULE main\n"
        
        ## VAR and INIT ##
        var_init_str = self.var_and_init(fsm_desc, filename)

        # Transition
        transition_str =  self.get_transition_relation()

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


    def var_and_init(self, fsm_desc, filename):
        ### VAR section ###
        var_str = "VAR\n"
        state_init_dict = {}
        for var in fsm_desc:
            state_type, init_value, next_fn = fsm_desc[var]

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


    def get_transition_relation(self):
        transiton_str = ""
#        (state_name, next_state_value, depend_event_name, depend_event_value)

#        assign_str  = assign_str + ' next(' +    

        # default  transition
#        assign_str = assign_str + '    TRUE : ' + var_name + ';\nesac;\n'


        return transiton_str

    def feed_to_nusmv(self, path_to_file):
        p = subprocess.Popen([self.exec_cmd, '-r', path_to_file], stdout=subprocess.PIPE) 
        out, err = p.communicate()

        print out
