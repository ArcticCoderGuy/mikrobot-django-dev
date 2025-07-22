import React, { useEffect, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { 
  TrendingUp, 
  Shield, 
  Zap, 
  Users, 
  ChevronRight, 
  Star,
  ArrowUp,
  Brain,
  Target,
  Sparkles
} from 'lucide-react';

const HomePage = () => {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 300], [0, -50]);
  const y2 = useTransform(scrollY, [0, 300], [0, -100]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0.8]);

  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div 
          style={{ y: y1 }}
          className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-r from-blue-400/30 to-purple-600/30 rounded-full blur-3xl"
        />
        <motion.div 
          style={{ y: y2 }}
          className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-r from-cyan-400/20 to-blue-600/20 rounded-full blur-3xl"
        />
        <div className="absolute top-1/3 left-1/4 w-64 h-64 bg-gradient-to-r from-indigo-400/10 to-purple-600/10 rounded-full blur-2xl animate-pulse" />
      </div>

      {/* Hero Section */}
      <motion.section 
        style={{ opacity }}
        className="relative z-10 min-h-screen flex items-center justify-center px-6"
      >
        <div className="max-w-7xl mx-auto text-center">
          {/* Glass Card Container */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={isVisible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 1, ease: "easeOut" }}
            className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-12 shadow-2xl"
          >
            {/* Logo */}
            <motion.div
              initial={{ scale: 0 }}
              animate={isVisible ? { scale: 1 } : {}}
              transition={{ duration: 0.8, delay: 0.2, type: "spring", stiffness: 100 }}
              className="mb-8"
            >
              <div className="w-24 h-24 mx-auto bg-gradient-to-br from-cyan-400 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Brain className="w-12 h-12 text-white" />
              </div>
            </motion.div>

            {/* Main Heading */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-6xl md:text-8xl font-thin text-white mb-6 leading-tight"
            >
              <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent">
                Mikro
              </span>
              <span className="font-light text-white">Bot</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={isVisible ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="text-xl md:text-2xl text-slate-300 mb-12 font-light tracking-wide max-w-3xl mx-auto"
            >
              Älykkään kaupankäynnin tulevaisuus. 
              <br />
              <span className="text-cyan-400">Microscale precision meets infinite possibilities.</span>
            </motion.p>

            {/* CTA Button */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={isVisible ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.8, delay: 0.8 }}
            >
              <motion.button
                whileHover={{ 
                  scale: 1.05,
                  boxShadow: "0 20px 40px rgba(59, 130, 246, 0.4)"
                }}
                whileTap={{ scale: 0.95 }}
                className="group relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl text-lg font-medium transition-all duration-300"
              >
                <span className="relative z-10 flex items-center">
                  Aloita matkasi
                  <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </motion.button>
            </motion.div>
          </motion.div>
        </div>
      </motion.section>

      {/* Vision Block */}
      <VisionSection />

      {/* Features Section */}
      <FeaturesSection />

      {/* Testimonials */}
      <TestimonialsSection />

      {/* Final CTA */}
      <FinalCTASection />

      {/* Footer */}
      <FooterSection />
    </div>
  );
};

const VisionSection = () => (
  <motion.section
    initial={{ opacity: 0 }}
    whileInView={{ opacity: 1 }}
    transition={{ duration: 1 }}
    className="relative py-32 px-6"
  >
    <div className="absolute inset-0">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-900/20 to-purple-900/20 backdrop-blur-sm" />
    </div>
    
    <div className="relative z-10 max-w-6xl mx-auto text-center">
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8 }}
        className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-12"
      >
        <Sparkles className="w-16 h-16 text-cyan-400 mx-auto mb-8" />
        <h2 className="text-4xl md:text-6xl font-thin text-white mb-8">
          Visiomme
        </h2>
        <p className="text-xl text-slate-300 leading-relaxed max-w-4xl mx-auto">
          Uskomme, että jokainen kauppias ansaitsee pääsyn instituutioiden tasoisiin työkaluihin. 
          MikroBot demokratisoi kvantitatiivisen kaupankäynnin ja tekee siitä saavutettavan kaikille.
        </p>
      </motion.div>
    </div>
  </motion.section>
);

const FeaturesSection = () => {
  const features = [
    {
      icon: TrendingUp,
      title: "AI-Optimoitu Kaupankäynti",
      description: "Kehittyneet algoritmit analysoivat markkinoita reaaliajassa ja optimoivat kaupankäyntistrategiat jatkuvasti."
    },
    {
      icon: Shield,
      title: "Riskinhallinta",
      description: "Monimutkainen riskinhallintajärjestelmä suojaa pääomaa älykkäillä stop-loss ja take-profit -mekanismeilla."
    },
    {
      icon: Zap,
      title: "Millisekunnin Nopeus",
      description: "Ultranopeaa toteutusta kehittyneillä algoritmeilla, jotka reagoivat markkinamuutoksiin välittömästi."
    },
    {
      icon: Target,
      title: "Microscale Precision",
      description: "Erikoistunut pieniin positiokokoihin maksimaalisen tehokkuuden saavuttamiseksi kaikilla markkinatiloilla."
    }
  ];

  return (
    <section className="py-32 px-6 relative">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-thin text-white mb-6">
            Ominaisuudet
          </h2>
          <p className="text-xl text-slate-400 max-w-3xl mx-auto">
            Kaupankäynnin tulevaisuus on täällä
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              whileHover={{ y: -10, scale: 1.02 }}
              className="group backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all duration-500"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <feature.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-semibold text-white mb-4">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

const TestimonialsSection = () => {
  const testimonials = [
    {
      name: "Mikael Virtanen",
      role: "Kvantitatiivinen analyytikko",
      content: "MikroBot muutti kaupankäyntini täysin. ROI parani 340% ensimmäisten kuukausien aikana.",
      rating: 5
    },
    {
      name: "Anna Korhonen",
      role: "Päätoiminen kauppias",
      content: "Riskinhallinta on ensiluokkaista. En ole koskaan tuntenut oloani näin varmaksi markkinoilla.",
      rating: 5
    },
    {
      name: "Jukka Nieminen",
      role: "Hedge Fund Manager",
      content: "Instituutiotason työkalut pienen kauppiaan käytössä. Tämä on vallankumous.",
      rating: 5
    }
  ];

  return (
    <section className="py-32 px-6 relative">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-thin text-white mb-6">
            Asiakkaiden ääni
          </h2>
          <p className="text-xl text-slate-400">
            Mitä käyttäjämme sanovat
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50, rotateX: -10 }}
              whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              whileHover={{ y: -5, rotateX: 2 }}
              className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8"
            >
              <div className="flex items-center mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                ))}
              </div>
              <p className="text-slate-300 text-lg mb-6 leading-relaxed">"{testimonial.content}"</p>
              <div>
                <p className="text-white font-semibold">{testimonial.name}</p>
                <p className="text-slate-400 text-sm">{testimonial.role}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

const FinalCTASection = () => (
  <motion.section
    initial={{ opacity: 0 }}
    whileInView={{ opacity: 1 }}
    transition={{ duration: 1 }}
    className="py-32 px-6 relative"
  >
    <div className="absolute inset-0">
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/30 via-blue-900/30 to-purple-900/30 backdrop-blur-sm" />
    </div>
    
    <div className="relative z-10 max-w-4xl mx-auto text-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        whileInView={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8 }}
        className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-12"
      >
        <h2 className="text-4xl md:text-6xl font-thin text-white mb-8">
          Valmis aloittamaan?
        </h2>
        <p className="text-xl text-slate-300 mb-12 leading-relaxed">
          Liity tuhansien kauppiaiden joukkoon, jotka ovat mullistaneet kaupankäyntinsä MikroBotilla.
        </p>
        
        <motion.button
          whileHover={{ 
            scale: 1.05,
            boxShadow: "0 25px 50px rgba(6, 182, 212, 0.5)"
          }}
          whileTap={{ scale: 0.95 }}
          className="group relative overflow-hidden bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-12 py-6 rounded-2xl text-xl font-semibold transition-all duration-300"
        >
          <span className="relative z-10 flex items-center">
            Aloita ilmainen kokeilu
            <ArrowUp className="ml-3 w-6 h-6 group-hover:translate-y-[-2px] group-hover:rotate-45 transition-transform" />
          </span>
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        </motion.button>
      </motion.div>
    </div>
  </motion.section>
);

const FooterSection = () => (
  <footer className="py-16 px-6 relative backdrop-blur-xl bg-black/20 border-t border-white/10">
    <div className="max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-center">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="flex items-center mb-8 md:mb-0"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-xl flex items-center justify-center mr-4">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-semibold text-white">MikroBot</h3>
            <p className="text-slate-400 text-sm">Smart Microscale Trading</p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center md:text-right"
        >
          <p className="text-slate-400 mb-2">Powered by</p>
          <p className="text-white font-semibold">Fox-In-The-Code</p>
          <p className="text-slate-500 text-sm mt-2">© 2025 All rights reserved</p>
        </motion.div>
      </div>
    </div>
  </footer>
);

export default HomePage;