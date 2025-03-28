import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
# from app.g4f.chat import get_chat
# import app.g4f.promts as promt

from app.database.requests import set_user, add_user, set_appointment
import app.keyboards as kb

router = Router()


class Reg(StatesGroup):
    name = State()
    last_name = State()
    contact = State()


class Appointment(StatesGroup):
    master = State()
    category = State()
    service = State()

class Navigation(StatesGroup):
    history = State()
    previous_function = State()
    data_object = State()
    data_object = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await set_user(message.from_user.id)
    if user:
        await message.answer(f'Приветствую, {user.name}!', reply_markup=kb.main)
        await state.clear()
    else:
        await message.answer(
            f"Рад с Вами познакомиться, {message.from_user.username}!\n\n"
            "Давайте пройдем короткую регистрацию, чтобы я запомнил Вас как нашего клиента❤️\n\n"
            "Напишите своё <b>ИМЯ</b>",
            parse_mode="HTML"
        )
        await state.set_state(Reg.name)


@router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.last_name)
    await message.answer('Теперь напишите <b>ФАМИЛИЮ</b>', parse_mode="HTML")

@router.message(Reg.last_name)
async def reg_lastname(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(Reg.contact)
    await message.answer('Отправьте номер телефона', reply_markup=kb.contact)


@router.message(Reg.contact, F.contact)
async def reg_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    print(message.from_user.id, data['name'], data['last_name'], message.contact.phone_number)
    await add_user(message.from_user.id, data['name'], data['last_name'], message.contact.phone_number)
    await state.clear()
    await message.answer(f'Супер! Теперь Вам открыто меню задач.', reply_markup=kb.main)
    await message.answer("Выберите действие:", reply_markup=kb.menu)


@router.message(F.text == 'Меню')
async def menu(message: Message, state: FSMContext):
    await message.answer("Выберите действие:", reply_markup=kb.menu)



# ----------кнопка ПОСМОТРЕТЬ ЦЕНЫ -----------
@router.callback_query(F.data == 'view_prices')
async def view_prices(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    photo_path = os.path.join('app', 'media', 'img', 'price.jpg')
    await callback.message.answer_photo(photo=FSInputFile(photo_path), caption="Прайс-лист", reply_markup=kb.back)


    


# --------кнопка ЗАПИСАТЬСЯ НА УСЛУГУ ---------
@router.callback_query(F.data == 'book_service')
async def get_master(callback: CallbackQuery, state: FSMContext):

    await state.set_state(Appointment.master)
    await callback.message.answer('Выберите мастера', reply_markup=await kb.masters())

 


# --------кнопка ВЫбора КАТЕГОРИИ ---------
@router.callback_query(F.data.startswith('master_'), Appointment.master)
async def get_category(callback: CallbackQuery, state: FSMContext):
        
    await callback.answer('Мастер выбран.')
    await state.update_data(master=callback.data.split('_')[1])
    await state.set_state(Appointment.category)
    await callback.message.answer('Выберите категорию', reply_markup=await kb.categories())


# --------кнопка ВЫбОРА УСЛУГИ ---------
@router.callback_query(F.data.startswith('category_'), Appointment.category)
async def get_service(callback: CallbackQuery, state: FSMContext):
    
    await callback.answer('Категория выбрана.')
    await state.update_data(category=callback.data.split('_')[1])
    await state.set_state(Appointment.service)
    await callback.message.answer('Выберите услугу', reply_markup=await kb.services(callback.data.split('_')[1]))
   


@router.callback_query(F.data.startswith('service_'), Appointment.service)
async def get_service_finish(callback: CallbackQuery, state: FSMContext):
   
    await callback.answer('Услуга выбрана.')
    data = await state.get_data()
    await set_appointment(callback.from_user.id, data['master'], callback.data.split('_')[1])
    await callback.message.answer('Вы успешно записаны!.', reply_markup=kb.main)
 

