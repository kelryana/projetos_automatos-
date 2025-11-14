import unittest
try:
    from afn_afd import AFD, AFN, PREDEFINED_AUTOMATA
except ImportError:
    raise ImportError("Certifique-se de que este ficheiro de teste está na mesma pasta que 'afn_afd.py'")

class TestAutomatonValidation(unittest.TestCase):

    def setUp(self):
        self.automata = {}
        
        afd_data_1 = PREDEFINED_AUTOMATA["AFD: L = a*b+a+b* "]
        self.automata["afd_1"] = AFD(afd_data_1["Q"], afd_data_1["Sigma"], afd_data_1["delta"], afd_data_1["q0"], afd_data_1["F"])

        afd_data_2 = PREDEFINED_AUTOMATA["AFD: L = 0(0|1)*1"]
        self.automata["afd_2"] = AFD(afd_data_2["Q"], afd_data_2["Sigma"], afd_data_2["delta"], afd_data_2["q0"], afd_data_2["F"])

        afn_data_1 = PREDEFINED_AUTOMATA["AFN (com ε): L = 0*1*2* "]
        self.automata["afn_1"] = AFN(afn_data_1["Q"], afn_data_1["Sigma"], afn_data_1["delta"], afn_data_1["q0"], afn_data_1["F"])

        afn_data_2 = PREDEFINED_AUTOMATA["AFN (com ε): Conversão )"]
        self.automata["afn_2"] = AFN(afn_data_2["Q"], afn_data_2["Sigma"], afn_data_2["delta"], afn_data_2["q0"], afn_data_2["F"])

    def test_afd_1_aceitas(self):
        afd = self.automata["afd_1"]
        cadeias_aceitas = ["ba", "aaba", "bbbbba", "baab", "bababab"]
        for cadeia in cadeias_aceitas:
            with self.subTest(cadeia=cadeia):
                self.assertTrue(afd.validate(cadeia)[0], f"Deveria aceitar: '{cadeia}'")

    def test_afd_1_rejeitadas(self):
        afd = self.automata["afd_1"]
        cadeias_rejeitadas = ["", "a", "b", "abb", "babbab", "bb"]
        for cadeia in cadeias_rejeitadas:
            with self.subTest(cadeia=cadeia):
                self.assertFalse(afd.validate(cadeia)[0], f"Deveria rejeitar: '{cadeia}'")

    def test_afd_2_aceitas(self):
        afd = self.automata["afd_2"]
        cadeias_aceitas = ["01", "001", "011", "0101", "00011101"]
        for cadeia in cadeias_aceitas:
            with self.subTest(cadeia=cadeia):
                self.assertTrue(afd.validate(cadeia)[0], f"Deveria aceitar: '{cadeia}'")

    def test_afd_2_rejeitadas(self):
        afd = self.automata["afd_2"]
        cadeias_rejeitadas = ["", "0", "1", "00", "010", "101", "0100"]
        for cadeia in cadeias_rejeitadas:
            with self.subTest(cadeia=cadeia):
                self.assertFalse(afd.validate(cadeia)[0], f"Deveria rejeitar: '{cadeia}'")

    def test_afn_1_aceitas(self):
        afn = self.automata["afn_1"]
        cadeias_aceitas = ["", "0", "1", "2", "00", "11", "22", "012", "0011122", "02", "12"]
        for cadeia in cadeias_aceitas:
            with self.subTest(cadeia=cadeia):
                self.assertTrue(afn.validate(cadeia)[0], f"Deveria aceitar: '{cadeia}'")

    def test_afn_1_rejeitadas(self):
        afn = self.automata["afn_1"]
        cadeias_rejeitadas = ["10", "210", "0121", "a", "01a2", "21"]
        for cadeia in cadeias_rejeitadas:
            with self.subTest(cadeia=cadeia):
                self.assertFalse(afn.validate(cadeia)[0], f"Deveria rejeitar: '{cadeia}'")

    def test_afn_2_aceitas(self):
        afn = self.automata["afn_2"]
        cadeias_aceitas = ["1", "01", "001", "101", "0101", "00010101"]
        for cadeia in cadeias_aceitas:
            with self.subTest(cadeia=cadeia):
                self.assertTrue(afn.validate(cadeia)[0], f"Deveria aceitar: '{cadeia}'")

    def test_afn_2_rejeitadas(self):
        afn = self.automata["afn_2"]
        cadeias_rejeitadas = ["", "0", "10", "11", "010", "0110"]
        for cadeia in cadeias_rejeitadas:
            with self.subTest(cadeia=cadeia):
                self.assertFalse(afn.validate(cadeia)[0], f"Deveria rejeitar: '{cadeia}'")

    def test_conversao_afn_1 (self):
        afn = self.automata["afn_1"]
        afd_convertido = afn.convert_to_afd()

        print("\n--- Testando AFD Convertido (L = 0*1*2*) ---")
        
        cadeias_aceitas = ["", "0", "1", "2", "00", "11", "22", "012", "0011122", "02", "12"]
        for cadeia in cadeias_aceitas:
            with self.subTest(cadeia=cadeia, tipo="AFD Convertido (Aceita)"):
                self.assertTrue(afd_convertido.validate(cadeia)[0], f"AFD Convertido deveria aceitar: '{cadeia}'")
        
        cadeias_rejeitadas = ["10", "210", "0121", "a", "01a2", "21"]
        for cadeia in cadeias_rejeitadas:
            with self.subTest(cadeia=cadeia, tipo="AFD Convertido (Rejeita)"):
                self.assertFalse(afd_convertido.validate(cadeia)[0], f"AFD Convertido deveria rejeitar: '{cadeia}'")

    def test_conversao_afn_2(self):
        afn = self.automata["afn_2"]
        afd_convertido = afn.convert_to_afd()

        print("\n--- Testando AFD Convertido (Conversão L=0*1(01)*) ---")
        
        cadeias_aceitas = ["1", "01", "001", "101", "0101", "00010101"]
        for cadeia in cadeias_aceitas:
            with self.subTest(cadeia=cadeia, tipo="AFD Convertido (Aceita)"):
                self.assertTrue(afd_convertido.validate(cadeia)[0], f"AFD Convertido deveria aceitar: '{cadeia}'")
        
        cadeias_rejeitadas = ["", "0", "10", "11", "010", "0110"]
        for cadeia in cadeias_rejeitadas:
            with self.subTest(cadeia=cadeia, tipo="AFD Convertido (Rejeita)"):
                self.assertFalse(afd_convertido.validate(cadeia)[0], f"AFD Convertido deveria rejeitar: '{cadeia}'")

if __name__ == '__main__':
    unittest.main()